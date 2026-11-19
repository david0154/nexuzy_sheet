# Nexuzy Sheet installers

This directory contains everything that is needed to generate native
installers for **Windows**, **macOS** and **Linux**.

Nexuzy Sheet is a Python/Qt application, so the bundles are created with
[PyInstaller](https://pyinstaller.org) and then wrapped into platform specific
installers:

| Platform | Artifact | Tool |
| --- | --- | --- |
| Windows | `Nexuzy-Sheet-<version>-windows-x64-setup.exe` | [Inno Setup 6](https://jrsoftware.org/isinfo.php) |
| Windows | `Nexuzy-Sheet-<version>-windows-x64.zip` (portable) | zip |
| macOS | `Nexuzy-Sheet-<version>-macos.dmg` | `hdiutil` |
| macOS | `Nexuzy-Sheet-<version>-macos.zip` (app bundle) | `ditto` |
| Linux | `Nexuzy-Sheet-<version>-linux-x86_64.AppImage` | `appimagetool` |
| Linux | `Nexuzy-Sheet-<version>-linux-amd64.deb` | `dpkg-deb` |
| Linux | `Nexuzy-Sheet-<version>-linux.tar.gz` (portable) | tar |

## Quick start

```bash
python -m pip install pyinstaller
python build_installers.py
```

The script bundles the application with `installers/nxsheet.spec` and then
packages the result for the operating system it runs on. All artifacts are
written to `dist/installers/`.

Options:

```text
--platform {windows,macos,linux}   target platform (default: this machine)
--clean                            remove build/ and dist/ before bundling
--skip-bundle                      only package an existing dist/ bundle
--no-native                        only create portable archives
```

`PyInstaller` cannot cross-compile. To create installers for all three
operating systems, run the workflow in
`.github/workflows/build-installers.yml`, which builds on Windows, macOS and
Ubuntu runners in parallel.

## Manual step by step

### Windows

```powershell
python -m pip install pyinstaller
python build_installers.py --platform windows
```

If Inno Setup is installed, the setup executable is created automatically.
Otherwise install it from <https://jrsoftware.org/isinfo.php> and compile
`installers/windows/nexuzy_sheet.iss`, or run:

```powershell
iscc /DMyAppVersion=1.2.0 installers\windows\nexuzy_sheet.iss
```

### macOS

```bash
python3 -m pip install pyinstaller
python3 build_installers.py --platform macos
```

This creates `dist/Nexuzy Sheet.app` and the DMG. The app bundle is unsigned;
for distribution outside your own machine sign it with `codesign` and
notarize it with `notarytool`.

### Linux

```bash
python3 -m pip install pyinstaller
python3 build_installers.py --platform linux
```

Standalone helpers are available as well:

```bash
./installers/linux/build_appimage.sh
./installers/linux/build_deb.sh
```

`build_appimage.sh` needs `appimagetool` in `PATH`. `build_deb.sh` needs
`dpkg-deb` (Debian/Ubuntu).

## Bundle contents

`installers/nxsheet.spec` bundles

- the frozen Python runtime and all dependencies (PyQt6, numpy, markdown2, …),
- `nxsheet/share` with icons, documentation and chart templates,
- `LICENSE`, `README.md` and `changelog`.

Application metadata (name, version, company, website) is defined once in
`nxsheet/__init__.py` and read by the build script and the spec file.

## License

Nexuzy Sheet is released under the MIT License. Copyright (c) 2026
Nexuzy Lab, <https://nexuzy.in>.
