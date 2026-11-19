# -*- mode: python ; coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# PyInstaller specification file for Nexuzy Sheet.
# Build with:  python build_installers.py
# --------------------------------------------------------------------

import sys
from importlib.util import find_spec
from pathlib import Path

ROOT = Path(SPECPATH).resolve().parent
SHARE = ROOT / "nxsheet" / "share"
ASSETS = ROOT / "nxsheet" / "assets"
ICON_ICO = ASSETS / "icon.ico"
ICON_PNG = ASSETS / "logo.png"
ICON_ICNS = ASSETS / "icon.icns"


def app_version() -> str:
    """Returns the version string from nxsheet/__init__.py"""

    init = ROOT / "nxsheet" / "__init__.py"
    for line in init.read_text(encoding="utf-8").splitlines():
        if line.startswith("VERSION"):
            return line.split("=", 1)[1].strip().strip('"')
    return "0.0.0"


datas = []

if SHARE.is_dir():
    datas.append((str(SHARE), "nxsheet/share"))
if ASSETS.is_dir():
    datas.append((str(ASSETS), "nxsheet/assets"))
if ICON_ICO.is_file():
    datas.append((str(ICON_ICO), "."))
for filename in ("LICENSE", "README.md", "changelog",
                 "THIRD_PARTY_LICENSES.md"):
    path = ROOT / filename
    if path.is_file():
        datas.append((str(path), "."))
DOCS = ROOT / "docs"
if DOCS.is_dir():
    datas.append((str(DOCS), "docs"))


hiddenimports = [
    "nxsheet",
    "nxsheet.main",
    "nxsheet.main_window",
    "nxsheet.actions",
    "nxsheet.commands",
    "nxsheet.dialogs",
    "nxsheet.grid",
    "nxsheet.grid_renderer",
    "nxsheet.icons",
    "nxsheet.installer",
    "nxsheet.i18n",
    "nxsheet.autosave",
    "nxsheet.menus",
    "nxsheet.panels",
    "nxsheet.settings",
    "nxsheet.templates",
    "nxsheet.themes",
    "nxsheet.toolbar",
    "nxsheet.widgets",
    "nxsheet.workflows",
    "nxsheet.ai.engine",
    "huggingface_hub",
    "huggingface_hub.file_download",
    "huggingface_hub.utils",
    "PyQt6.QtCore",
    "PyQt6.QtGui",
    "nxsheet.interfaces.pys",
    "nxsheet.interfaces.xlsx",
    "nxsheet.lib.excel_functions",
    "nxsheet.model.model",
    "PyQt6.QtSvg",
    "PyQt6.QtSvgWidgets",
    "PyQt6.QtPrintSupport",
    "PyQt6.QtNetwork",
    "PyQt6.QtXml",
    "numpy",
    "markdown2",
]

# Optional features are bundled only when they are installed. They are all
# imported inside try/except blocks, so the application runs without them.
for optional in ("openpyxl", "pycel", "moneyed", "dateutil", "fitz",
                 "pymupdf", "enchant", "matplotlib", "matplotlib.pyplot",
                 "odf", "xlwt"):
    try:
        if find_spec(optional):
            hiddenimports.append(optional)
    except (ImportError, ValueError):
        pass

# PyInstaller may omit distribution metadata. Preserve metadata for installed
# modules so the in-app dependency list can display exact versions.
try:
    from importlib.metadata import distribution, packages_distributions
    _package_map = packages_distributions()
    _import_names = {"markdown2": "markdown2", "numpy": "numpy",
                     "PyQt6": "PyQt6", "matplotlib": "matplotlib",
                     "openpyxl": "openpyxl", "plotnine": "plotnine",
                     "pycel": "pycel", "python-dateutil": "dateutil",
                     "pyenchant": "enchant", "py-moneyed": "moneyed",
                     "rpy2": "rpy2"}
    for _distribution, _import_name in _import_names.items():
        _dist_names = _package_map.get(_import_name, [])
        if not _dist_names:
            _dist_names = [_distribution]
        for _dist_name in _dist_names:
            try:
                _dist = distribution(_dist_name)
                datas.extend((str(_dist.locate_file(_file)),
                              f"{_dist_name}.dist-info")
                             for _file in (_dist.files or [])
                             if str(_file).upper().endswith("METADATA"))
            except Exception:
                pass
except ImportError:
    pass

# PyInstaller does not reliably collect the Python runtime DLL on newer
# CPython releases (seen with Python 3.14). Add it explicitly, resolved from
# the interpreter that runs this build instead of a hardcoded path, and pull
# in the stable ABI DLL and the MSVC runtime that sits next to it.
binaries = []
if sys.platform.startswith("win"):
    _base = Path(sys.base_prefix)
    for _dll in (
        _base / f"python{sys.version_info.major}{sys.version_info.minor}.dll",
        _base / "python3.dll",
        _base / "vcruntime140.dll",
        _base / "vcruntime140_1.dll",
    ):
        if _dll.is_file():
            binaries.append((str(_dll), "."))

a = Analysis(
    [str(ROOT / "installers" / "launcher.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude large training stacks. Local inference runs through the
        # llama.cpp binary that the app installs at setup time.
        "torch", "torchvision", "torchaudio", "transformers",
        "tensorflow", "keras", "scipy", "sklearn", "pandas", "cv2",
        "easyocr", "paddleocr", "paddle", "onnxruntime", "jax",
        "IPython", "jupyter", "notebook", "pytest", "tkinter",
        "matplotlib.backends._backend_tk", "PyQt5", "win32com",
        "pythoncom", "pywintypes",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

if sys.platform.startswith("win"):
    icon = str(ICON_ICO) if ICON_ICO.is_file() else None
elif sys.platform == "darwin":
    icon = str(ICON_ICNS) if ICON_ICNS.is_file() else None
else:
    icon = str(ICON_PNG) if ICON_PNG.is_file() else None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="nexuzy-sheet",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=icon,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="nexuzy-sheet",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Nexuzy Sheet.app",
        icon=str(ICON_ICNS) if ICON_ICNS.is_file() else None,
        bundle_identifier="io.nexuzy.nexuzysheet",
        version=app_version(),
        info_plist={
            "CFBundleDisplayName": "Nexuzy Sheet",
            "CFBundleName": "Nexuzy Sheet",
            "CFBundleShortVersionString": app_version(),
            "CFBundleVersion": app_version(),
            "CFBundleIdentifier": "io.nexuzy.nexuzysheet",
            "CFBundleDocumentTypes": [
                {
                    "CFBundleTypeName": "Nexuzy Sheet workbook",
                    "CFBundleTypeExtensions": ["nix", "nxl", "nxs"],
                    "CFBundleTypeRole": "Editor",
                }
            ],
            "NSHighResolutionCapable": True,
            "NSHumanReadableCopyright":
                "Copyright (c) 2026 Nexuzy Lab",
        },
    )
