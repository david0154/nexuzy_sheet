#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Generates native installers for Windows, macOS and Linux.
# Licensed under the MIT License.
# --------------------------------------------------------------------

"""Builds Nexuzy Sheet installers for Windows, macOS and Linux.

The script bundles the application with PyInstaller and wraps the result into
the native installer format of the current platform:

* Windows: portable zip and Inno Setup ``setup.exe``
* macOS: ``.app`` zip and ``.dmg`` disk image
* Linux: ``.tar.gz``, ``.deb`` and ``.AppImage``

Usage::

    python build_installers.py                  # current platform
    python build_installers.py --platform linux
    python build_installers.py --clean --no-native

"""

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
OUTPUT = DIST / "installers"
SPEC = ROOT / "installers" / "nxsheet.spec"
EXECUTABLE = "nexuzy-sheet"


def read_metadata(name: str, default: str) -> str:
    """Reads a string constant from nxsheet/__init__.py

    :param name: Name of the constant
    :param default: Fallback value if the constant is not present

    """

    init_path = ROOT / "nxsheet" / "__init__.py"
    try:
        lines = init_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return default
    for line in lines:
        if line.startswith(f"{name} ="):
            return line.split("=", 1)[1].strip().strip("\"'")
    return default


VERSION = read_metadata("VERSION", "0.0.0")
APP_NAME = read_metadata("APP_NAME", "Nexuzy Sheet")
COMPANY = read_metadata("COMPANY", "Nexuzy Lab")
COMPANY_URL = read_metadata("COMPANY_URL", "https://nexuzy.in")


def current_platform() -> str:
    """Returns the installer platform of the running machine"""

    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def machine() -> str:
    """Returns a normalized architecture string"""

    return platform.machine().lower() or "x86_64"


def run(command) -> subprocess.CompletedProcess:
    """Runs a command and returns the completed process"""

    printable = " ".join(str(part) for part in command)
    print(f"  > {printable}", flush=True)
    return subprocess.run([str(part) for part in command], check=True)


def ensure_macos_icon() -> None:
    """Creates nxsheet/assets/icon.icns from logo.png on macOS"""

    icns = ROOT / "nxsheet" / "assets" / "icon.icns"
    png = ROOT / "nxsheet" / "assets" / "logo.png"

    if icns.is_file() or not png.is_file():
        return
    if not shutil.which("sips") or not shutil.which("iconutil"):
        print("  sips/iconutil not found - keeping the default app icon.")
        return

    iconset = BUILD / "nxsheet.iconset"
    shutil.rmtree(iconset, ignore_errors=True)
    iconset.mkdir(parents=True, exist_ok=True)

    for size in (16, 32, 64, 128, 256, 512):
        for scale in (1, 2):
            pixels = size * scale
            name = f"icon_{size}x{size}"
            if scale == 2:
                name += "@2x"
            subprocess.run(["sips", "-z", str(pixels), str(pixels), str(png),
                            "--out", str(iconset / f"{name}.png")],
                           check=True, capture_output=True)

    subprocess.run(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)],
                   check=True)
    shutil.rmtree(iconset, ignore_errors=True)
    print(f"  Created {icns}")


def require_pyinstaller() -> None:
    """Aborts if PyInstaller is not installed"""

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        sys.exit("PyInstaller is missing. Install it with:\n"
                 "    python -m pip install pyinstaller")


def bundle(clean: bool = False) -> Path:
    """Bundles the application with PyInstaller

    :param clean: Remove previous build output before bundling

    """

    require_pyinstaller()

    if current_platform() == "macos":
        ensure_macos_icon()

    if clean:
        print("Cleaning previous build output ...")
        for path in (BUILD, DIST):
            shutil.rmtree(path, ignore_errors=True)

    if not SPEC.is_file():
        sys.exit(f"Spec file not found: {SPEC}")

    DIST.mkdir(parents=True, exist_ok=True)

    print(f"Bundling {APP_NAME} {VERSION} ...")
    run([sys.executable, "-m", "PyInstaller", str(SPEC),
         "--noconfirm", "--distpath", str(DIST), "--workpath", str(BUILD)])

    bundle_dir = DIST / EXECUTABLE
    if current_platform() == "macos":
        app_bundle = DIST / f"{APP_NAME}.app"
        if app_bundle.is_dir():
            return app_bundle

    if not bundle_dir.is_dir():
        sys.exit(f"Bundling failed: {bundle_dir} was not created.")

    return bundle_dir


def copy_extras(target: Path) -> None:
    """Copies license and documentation next to the executable"""

    for filename in ("LICENSE", "README.md", "changelog",
                     "THIRD_PARTY_LICENSES.md"):
        source = ROOT / filename
        if source.is_file():
            shutil.copy2(source, target / filename)

    docs_source = ROOT / "docs"
    if docs_source.is_dir():
        shutil.copytree(docs_source, target / "docs", dirs_exist_ok=True)


def prepare_license_page(bundle_path: Path) -> Path:
    """Writes the plain-text EULA shown on the Windows installer page

    :param bundle_path: Path of the PyInstaller bundle directory

    """

    source = ROOT / "docs" / "EULA.md"
    if not source.is_file():
        return bundle_path / "LICENSE"
    text = source.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^#{1,6}\s*", "", text)
    text = text.replace("**", "").replace("`", "")
    target = bundle_path / "EULA.txt"
    target.write_text(text, encoding="utf-8-sig")
    return target


def find_inno_setup():
    """Returns the path of the Inno Setup compiler if it is installed"""

    candidates = [shutil.which("iscc"), shutil.which("ISCC")]
    for variable in ("ProgramFiles(x86)", "ProgramFiles"):
        base = os.environ.get(variable)
        if base:
            for name in ("Inno Setup 6", "Inno Setup 5"):
                candidates.append(Path(base) / name / "ISCC.exe")

    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    return None


def package_windows(bundle_path: Path, native: bool = True) -> list:
    """Packages the Windows bundle as zip and Inno Setup installer"""

    artifacts = []
    OUTPUT.mkdir(parents=True, exist_ok=True)

    license_page = prepare_license_page(bundle_path)
    arch = "x64" if machine() in ("x86_64", "amd64") else machine()
    stem = OUTPUT / f"{APP_NAME.replace(' ', '-')}-{VERSION}-windows-{arch}"
    archive = shutil.make_archive(str(stem), "zip",
                                  root_dir=str(bundle_path.parent),
                                  base_dir=bundle_path.name)
    artifacts.append(Path(archive))
    print(f"  Created {archive}")

    if not native:
        return artifacts

    iscc = find_inno_setup()
    if iscc is None:
        print("  Inno Setup was not found - skipping setup.exe.")
        print("  Install Inno Setup 6 from https://jrsoftware.org/isinfo.php")
        return artifacts

    run([iscc,
         f"/DMyAppVersion={VERSION}",
         f"/DMyAppName={APP_NAME}",
         f"/DSourceDir={bundle_path}",
         f"/DLicenseFile={license_page}",
         f"/DOutputDir={OUTPUT}",
         str(ROOT / "installers" / "windows" / "nexuzy_sheet.iss")])
    setup_path = OUTPUT / f"{APP_NAME.replace(' ', '-')}-{VERSION}-windows-{arch}-setup.exe"
    if setup_path.is_file():
        artifacts.append(setup_path)
        print(f"  Created {setup_path}")
    else:
        print(f"  Inno Setup did not create {setup_path.name}")
    return artifacts


def package_macos(bundle_path: Path, native: bool = True) -> list:
    """Packages the macOS app bundle as zip and disk image"""

    artifacts = []
    OUTPUT.mkdir(parents=True, exist_ok=True)

    app_path = bundle_path
    if app_path.suffix != ".app":
        app_path = DIST / f"{APP_NAME}.app"

    if not app_path.is_dir():
        sys.exit(f"App bundle not found: {app_path}")

    zip_path = OUTPUT / f"{APP_NAME.replace(' ', '-')}-{VERSION}-macos.zip"
    if zip_path.exists():
        zip_path.unlink()
    if shutil.which("ditto"):
        run(["ditto", "-c", "-k", "--sequesterRsrc", "--keepParent",
             str(app_path), str(zip_path)])
    else:
        archive = shutil.make_archive(str(zip_path.with_suffix("")), "zip",
                                      root_dir=str(app_path.parent),
                                      base_dir=app_path.name)
        zip_path = Path(archive)
    artifacts.append(zip_path)
    print(f"  Created {zip_path}")

    if not native:
        return artifacts

    if not shutil.which("hdiutil"):
        print("  hdiutil not found - skipping .dmg creation.")
        return artifacts

    script = ROOT / "installers" / "macos" / "build_dmg.sh"
    run(["bash", str(script), str(app_path), str(OUTPUT)])
    dmg_path = OUTPUT / f"{APP_NAME.replace(' ', '-')}-{VERSION}-macos.dmg"
    if dmg_path.is_file():
        artifacts.append(dmg_path)
    return artifacts


def build_deb(bundle_path: Path) -> Path:
    """Builds a Debian package from the Linux bundle

    :param bundle_path: Path of the PyInstaller bundle directory

    """

    if not shutil.which("dpkg-deb"):
        print("  dpkg-deb not found - skipping .deb package.")
        return None

    arch = {"x86_64": "amd64", "amd64": "amd64",
            "aarch64": "arm64", "arm64": "arm64"}.get(machine(), "amd64")
    package = f"{APP_NAME.replace(' ', '-').lower()}_{VERSION}_{arch}"
    staging = BUILD / package
    shutil.rmtree(staging, ignore_errors=True)

    install_dir = staging / "opt" / "nexuzy-sheet"
    shutil.copytree(bundle_path, install_dir)
    copy_extras(install_dir)

    (staging / "DEBIAN").mkdir(parents=True)
    (staging / "usr" / "bin").mkdir(parents=True)
    applications = staging / "usr" / "share" / "applications"
    applications.mkdir(parents=True)
    mime_packages = staging / "usr" / "share" / "mime" / "packages"
    mime_packages.mkdir(parents=True)
    icons = staging / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    icons.mkdir(parents=True)
    documentation = staging / "usr" / "share" / "doc" / "nexuzy-sheet"
    documentation.mkdir(parents=True)

    wrapper = staging / "usr" / "bin" / "nexuzy-sheet"
    wrapper.write_text("#!/bin/sh\nexec /opt/nexuzy-sheet/nexuzy-sheet \"$@\"\n",
                       encoding="utf-8")
    wrapper.chmod(0o755)

    desktop = ROOT / "installers" / "linux" / "nexuzy-sheet.desktop"
    if desktop.is_file():
        shutil.copy2(desktop, applications / "nexuzy-sheet.desktop")

    mime_source = ROOT / "installers" / "linux" / "nexuzy-sheet-mime.xml"
    if mime_source.is_file():
        shutil.copy2(mime_source, mime_packages / "nexuzy-sheet.xml")

    icon = ROOT / "nxsheet" / "assets" / "logo.png"
    if icon.is_file():
        shutil.copy2(icon, icons / "nexuzy-sheet.png")

    license_file = ROOT / "LICENSE"
    if license_file.is_file():
        shutil.copy2(license_file, documentation / "copyright")
    third_party = ROOT / "THIRD_PARTY_LICENSES.md"
    if third_party.is_file():
        shutil.copy2(third_party, documentation / "THIRD_PARTY_LICENSES.md")

    control = (
        f"Package: nexuzy-sheet\n"
        f"Version: {VERSION}\n"
        f"Section: office\n"
        f"Priority: optional\n"
        f"Architecture: {arch}\n"
        f"Maintainer: {COMPANY} <support@nexuzy.in>\n"
        f"Homepage: {COMPANY_URL}\n"
        f"Depends: libc6, libgl1, libegl1, libxkbcommon-x11-0, "
        f"libxcb-cursor0, shared-mime-info\n"
        f"Description: Excel-like spreadsheet workspace\n"
        f" Nexuzy Sheet is a spreadsheet application for business data,\n"
        f" templates, calculations, exports, charts and AI assisted workflows.\n"
    )
    (staging / "DEBIAN" / "control").write_text(control, encoding="utf-8")

    postinst = staging / "DEBIAN" / "postinst"
    postinst.write_text(
        "#!/bin/sh\n"
        "set -e\n"
        "if command -v update-mime-database >/dev/null 2>&1; then\n"
        "    update-mime-database /usr/share/mime || true\n"
        "fi\n"
        "if command -v update-desktop-database >/dev/null 2>&1; then\n"
        "    update-desktop-database /usr/share/applications || true\n"
        "fi\n",
        encoding="utf-8")
    postinst.chmod(0o755)

    deb_path = OUTPUT / f"{APP_NAME.replace(' ', '-')}-{VERSION}-linux-{arch}.deb"
    run(["dpkg-deb", "--root-owner-group", "--build", str(staging),
         str(deb_path)])
    return deb_path


def build_appimage(bundle_path: Path) -> Path:
    """Builds an AppImage from the Linux bundle

    :param bundle_path: Path of the PyInstaller bundle directory

    """

    tool = shutil.which("appimagetool")
    if tool is None:
        print("  appimagetool not found - skipping .AppImage creation.")
        print("  See https://github.com/AppImage/AppImageKit/releases")
        return None

    appdir = BUILD / "NexuzySheet.AppDir"
    shutil.rmtree(appdir, ignore_errors=True)
    (appdir / "usr" / "bin").mkdir(parents=True)
    (appdir / "usr" / "share" / "applications").mkdir(parents=True)
    (appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps"
     ).mkdir(parents=True)

    for item in bundle_path.iterdir():
        target = appdir / "usr" / "bin" / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)

    app_run = ROOT / "installers" / "linux" / "AppRun"
    if app_run.is_file():
        target = appdir / "AppRun"
        shutil.copy2(app_run, target)
        target.chmod(0o755)

    desktop = ROOT / "installers" / "linux" / "nexuzy-sheet.desktop"
    if desktop.is_file():
        shutil.copy2(desktop, appdir / "nexuzy-sheet.desktop")
        shutil.copy2(desktop,
                     appdir / "usr" / "share" / "applications"
                     / "nexuzy-sheet.desktop")

    mime_source = ROOT / "installers" / "linux" / "nexuzy-sheet-mime.xml"
    if mime_source.is_file():
        mime_dir = appdir / "usr" / "share" / "mime" / "packages"
        mime_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(mime_source, mime_dir / "nexuzy-sheet.xml")

    icon = ROOT / "nxsheet" / "assets" / "logo.png"
    if icon.is_file():
        shutil.copy2(icon, appdir / "nexuzy-sheet.png")
        shutil.copy2(icon, appdir / "usr" / "share" / "icons" / "hicolor"
                     / "256x256" / "apps" / "nexuzy-sheet.png")

    license_file = ROOT / "LICENSE"
    if license_file.is_file():
        shutil.copy2(license_file, appdir / "LICENSE")

    appimage_path = (OUTPUT /
                     f"{APP_NAME.replace(' ', '-')}-{VERSION}-linux-"
                     f"{machine()}.AppImage")
    environment = dict(os.environ)
    environment["ARCH"] = machine()
    printable = f"{tool} {appdir} {appimage_path}"
    print(f"  > {printable}", flush=True)
    subprocess.run([tool, str(appdir), str(appimage_path)], check=True,
                   env=environment)
    return appimage_path


def package_linux(bundle_path: Path, native: bool = True) -> list:
    """Packages the Linux bundle as tar.gz, deb and AppImage"""

    artifacts = []
    OUTPUT.mkdir(parents=True, exist_ok=True)

    stem = OUTPUT / f"{APP_NAME.replace(' ', '-')}-{VERSION}-linux-{machine()}"
    archive = shutil.make_archive(str(stem), "gztar",
                                  root_dir=str(bundle_path.parent),
                                  base_dir=bundle_path.name)
    artifacts.append(Path(archive))
    print(f"  Created {archive}")

    if not native:
        return artifacts

    deb = build_deb(bundle_path)
    if deb is not None:
        artifacts.append(deb)
        print(f"  Created {deb}")

    appimage = build_appimage(bundle_path)
    if appimage is not None:
        artifacts.append(appimage)
        print(f"  Created {appimage}")

    return artifacts


PACKAGERS = {
    "windows": package_windows,
    "macos": package_macos,
    "linux": package_linux,
}


def parse_arguments() -> argparse.Namespace:
    """Parses the command line arguments"""

    parser = argparse.ArgumentParser(
        prog="build_installers.py",
        description=f"Build {APP_NAME} {VERSION} installers.")
    parser.add_argument(
        "--platform", choices=("windows", "macos", "linux"),
        default=current_platform(),
        help="Target platform (default: this machine)")
    parser.add_argument(
        "--clean", action="store_true",
        help="Remove build/ and dist/ before bundling")
    parser.add_argument(
        "--skip-bundle", action="store_true",
        help="Package an existing bundle in dist/ without rebuilding it")
    parser.add_argument(
        "--no-native", action="store_true",
        help="Only create portable archives, no native installer")
    parser.add_argument(
        "--version", action="version", version=f"{APP_NAME} {VERSION}")
    return parser.parse_args()


def main() -> int:
    """Builds the installers and prints the created artifacts"""

    args = parse_arguments()

    if args.platform != current_platform():
        print(f"PyInstaller cannot cross-compile from {current_platform()} "
              f"to {args.platform}.", file=sys.stderr)
        print("Use .github/workflows/build-installers.yml or run this script "
              "on the target platform.", file=sys.stderr)
        return 2

    if args.skip_bundle:
        bundle_path = DIST / (f"{APP_NAME}.app"
                              if args.platform == "macos" else EXECUTABLE)
        if not bundle_path.exists():
            print(f"No bundle found at {bundle_path}. Run without "
                  "--skip-bundle first.", file=sys.stderr)
            return 2
        if bundle_path.is_dir() and args.platform != "macos":
            copy_extras(bundle_path)
    else:
        bundle_path = bundle(args.clean)
        if bundle_path.is_dir():
            copy_extras(bundle_path)

    print(f"\nPackaging for {args.platform} ...")
    artifacts = PACKAGERS[args.platform](bundle_path,
                                         native=not args.no_native)

    print("\nCreated artifacts:")
    for artifact in artifacts:
        print(f"  {artifact}")
    print("\nAll output is in", OUTPUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
