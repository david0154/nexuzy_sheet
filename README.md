# Nexuzy Sheet

**Nexuzy Sheet** is a free, open source spreadsheet workspace for Windows,
macOS and Linux. It combines an Excel-like interface with Python powered
cells, 107 spreadsheet functions, business templates, charts and local AI
assistance.

Developed and published by **Nexuzy Lab** — <https://nexuzy.in>  
Web app: <https://sheet.nexuzy.in> · GitHub: <https://github.com/david0154/nexuzy_sheet>

* **License:** MIT — free and open source, free to use forever
* **AI assistant:** **Nexuzy AI** — optional, runs offline with the Qwen2.5
  0.5B model and knows the complete built-in formula library
* **Native workbook format:** `.nix`
* **Languages:** English, हिन्दी, বাংলা, தமிழ், Español, Français, 中文,
  Русский, 日本語
* **Platforms:** Windows, macOS, Linux (desktop application)

---

## Contents

1. [Highlights](#highlights)
2. [Screens at a glance](#screens-at-a-glance)
3. [Install](#install)
4. [Run from source](#run-from-source)
5. [Workbook format, auto save and backups](#workbook-format-auto-save-and-backups)
6. [Languages](#languages)
7. [Spreadsheet functions](#spreadsheet-functions)
8. [Import and export](#import-and-export)
9. [Templates](#templates)
10. [Build installers for all platforms](#build-installers-for-all-platforms)
11. [Project layout](#project-layout)
12. [Documentation](#documentation)
13. [Feature status](#feature-status)
14. [License](#license)
15. [Support](#support)

---

## Highlights

* **Excel-like grid** with menus, dockable toolbars, entry line, table tabs,
  status bar statistics, dark and light themes, full screen and 18 zoom levels.
* **Python cells** – every cell is an expression, so `SUM(S[0:10, 2, 0])`,
  `IF(...)`, `VLOOKUP(...)` or any Python code works directly.
* **107 spreadsheet functions** across mathematical, statistical, logical,
  lookup, text, date, financial and information categories.
* **Business templates** – invoice, attendance register, general ledger,
  payroll sheet and budget planning.
* **Charts and images** inside cells through matplotlib and SVG.
* **`.nix` workbooks** – compressed, self contained, holds code, formatting,
  macros, images and charts.
* **Auto save** recovery copies every two minutes while there are unsaved
  changes, plus **automatic backups** and a **version history** dialog.
* **AutoFit** – column widths and row heights adapt to the cell content
  (`Format → AutoFit columns / AutoFit rows / AutoFit selection`).
* **Optional offline AI assistant** – Qwen2.5-0.5B-Instruct (about 490 MB)
  can generate spreadsheet actions from prompts using nearby workbook data.
  The model and inference runtime are loaded on demand; no cloud API key is used.
* **Nine interface languages** with live switching in `View → Language`.
* **Installer build system** for Windows, macOS and Linux with `.nix` file
  association on every platform.
* **MIT licensed**, free forever, no account and no subscription.

## Screens at a glance

| Area | What it does |
| --- | --- |
| Menu bar | File, Edit, View, Format, Macro, Help |
| Toolbars | Main, Format, Find, Macro — all dockable and hideable |
| Entry line | Formula and value editor of the current cell |
| Grid | The spreadsheet with four synchronised views |
| Table tabs | The worksheets of the workbook |
| Macro panel | Python code that is stored inside the workbook |
| Status bar | Sum, average, count, min, max, zoom state, safe mode |

## Install

Download the installer for your platform from the release page:

| Platform | Artifact | Installer |
| --- | --- | --- |
| Windows x64 | `Nexuzy-Sheet-<version>-windows-x64-setup.exe` | Inno Setup, optional `.nix` association |
| Windows x64 (portable) | `Nexuzy-Sheet-<version>-windows-x64.zip` | unpack and run `nexuzy-sheet.exe` |
| macOS | `Nexuzy-Sheet-<version>-macos.dmg` | drag into *Applications* |
| Linux | `Nexuzy-Sheet-<version>-linux-x86_64.AppImage` | `chmod +x` and run |
| Debian/Ubuntu | `Nexuzy-Sheet-<version>-linux-amd64.deb` | `sudo dpkg -i …` |
| Linux (portable) | `Nexuzy-Sheet-<version>-linux-x86_64.tar.gz` | unpack and run |

All installers are generated from this repository with
[`build_installers.py`](build_installers.py); see
[Build installers](#build-installers-for-all-platforms).

## Run from source

Requirements: Python 3.8 or newer (tested with Python 3.14 on Windows) and a
desktop session.

```bash
<<<<<<< HEAD
git clone https://github.com/david0154/nexuzy-sheet.git
cd nexuzy-sheet
=======
git https://github.com/david0154/nexuzy-sheet.git
cd nexuzy-sheet
```
>>>>>>> c488941466627dc306aeb63ddb5a67682561d9dc

python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m nxsheet
```

Optional extras:

```bash
python -m pip install -r nxsheet/optional_ai_requirements.txt   # Offline Qwen inference + optional OCR
python -m pip install openpyxl xlwt odfpy                       # XLSX/XLS/ODS support
```

Open a workbook from the command line:

```bash
python -m nxsheet "C:/Work/Report.nix"
```

## Workbook format, auto save and backups

Nexuzy Sheet saves workbooks as **`.nix`** by default. The format stores cell
code, formatting, row heights, column widths, macros, images and charts,
compressed with bzip2. `.nxl` (uncompressed) and `.nxs` (compressed) from older
builds are still read and can still be written.

| Safety feature | Behaviour |
| --- | --- |
| Auto save | Recovery copy every 120 s while there are unsaved changes → `~/.nexuzy_sheet/autosave` |
| Automatic backup | After every save → `~/.nexuzy_sheet/backups/<workbook>/`, newest 20 kept |
| Close protection | A final recovery copy is written when closing with unsaved changes |
| Version history | `File → Version history…` lists, restores and deletes recovery copies and backups |

`.nix` is a **compressed, not encrypted** container; see
[docs/FILE_FORMAT.md](docs/FILE_FORMAT.md) for the format description and the
reader/writer example.

## Languages

The interface language is switched live in `View → Language` and stored for
the next start:

| Code | Language | Native name |
| --- | --- | --- |
| `en` | English | English |
| `hi` | Hindi | हिन्दी |
| `bn` | Bengali | বাংলা |
| `ta` | Tamil | தமிழ் |
| `es` | Spanish | Español |
| `fr` | French | Français |
| `zh` | Chinese | 中文 |
| `ru` | Russian | Русский |
| `ja` | Japanese | 日本語 |

Translations live in [`nxsheet/i18n.py`](nxsheet/i18n.py) and cover the menus,
the common actions and the About dialog. A string that has no entry stays in
English, so a partially translated build is still fully usable. Adding a
language is one dictionary entry plus its 65 source strings.

## Spreadsheet functions

Functions are typed directly into cells and accept cell ranges, numpy arrays,
lists and generators:

```python
SUM(S[0:10, 0, 0])
AVERAGE(S[1:5, 2, 0])
IF(S[0, 0, 0] > 100, "high", "low")
VLOOKUP("Apple", S[0:20, 0:2, 0], 2, False)
TEXT(S[0, 1, 0], "#,##0.00")
PMT(0.05/12, 60, -10000)
```

`Shift+F3` opens the searchable function catalog with signatures. The full
list of 107 functions and the functions that are **not** implemented yet is in
[docs/FEATURES.md](docs/FEATURES.md).

## Import and export

| Format | Import | Export |
| --- | --- | --- |
| `.nix` (native) | ✅ | ✅ |
| `.nxl`, `.nxs` (legacy native) | ✅ | ✅ |
| XLSX | ✅ (`openpyxl`) | ✅ |
| XLS | — | ✅ (`xlwt`) |
| CSV | ✅ | ✅ |
| TSV | ✅ | ✅ |
| ODS | — | ✅ (`odfpy`) |
| PDF | — | ✅ |
| HTML | — | ✅ |
| JSON | — | ✅ |
| TXT | — | ✅ |
| SVG | — | ✅ |
| PNG / JPG (cell images and charts) | — | ✅ |

## Templates

Five ready-made business templates are built in
([`nxsheet/templates.py`](nxsheet/templates.py)):

* Invoice
* Attendance Register
* General Ledger
* Payroll Sheet
* Budget Planning

Each template brings headers, sample data, merged title areas, number columns
and a styling configuration.

## AI tools and optional model download

The AI panel uses the optional offline Qwen2.5-0.5B-Instruct GGUF model to
interpret spreadsheet prompts, inspect a bounded snapshot around the active
cell, and create tables or formulas. Generated table actions can apply built-in
title/header formatting. The model loads only when a prompt is submitted, and
inference runs in a background thread so the UI remains responsive.

The assistant is given application information: Nexuzy Sheet is a desktop
spreadsheet app developed and published by **Nexuzy Lab**. It supports `.nix`
workbooks, multiple sheets, formulas and Python-powered cells, formatting,
templates, charts, and file import/export. It can refer users to the web app
<https://sheet.nexuzy.in> and source repository
<https://github.com/david0154/nexuzy_sheet>. Answers about features should be
limited to what the app actually supports.

To enable AI, use the AI model information dialog's **Download now** action.
Setup runs in the background and reuses a valid model already in
`~/.nexuzy_sheet/models/`; it downloads only when the file is missing or
incomplete. It also installs the llama.cpp CPU inference runtime (about 25 MB)
once, because the older `ctransformers` engine cannot load Qwen2 models. The
roughly 490 MB model weights are not bundled and are never downloaded
automatically. All inference is local; no account or
API key is used. The 0.5B model is small, so results may be inaccurate; review
generated cells before relying on them.

## Build installers for all platforms

The repository builds native installers for **Windows, macOS and Linux**. The
application is bundled with PyInstaller and wrapped in the platform's native
installer format.

```bash
python -m pip install -r requirements.txt pyinstaller
python build_installers.py                 # build for the current OS
python build_installers.py --platform windows
python build_installers.py --platform macos
python build_installers.py --platform linux
python build_installers.py --clean         # clean build
python build_installers.py --no-native     # portable archives only
```

| Platform | Artifacts produced |
| --- | --- |
| Windows | `dist/installers/Nexuzy-Sheet-<version>-windows-x64.zip`, `…-setup.exe` (Inno Setup 6, includes `.nix` association) |
| macOS | `dist/installers/Nexuzy-Sheet-<version>-macos.zip`, `…-macos.dmg` (`hdiutil`) |
| Linux | `dist/installers/Nexuzy-Sheet-<version>-linux-<arch>.tar.gz`, `.deb` (`dpkg-deb`, includes desktop entry + MIME type), `.AppImage` (`appimagetool`) |

PyInstaller cannot cross compile: `--platform` selects packaging logic but
does not turn a Windows build into a macOS or Linux binary. Build each target
on its native OS, or use the repository CI workflow
[`.github/workflows/build-installers.yml`](.github/workflows/build-installers.yml)
to build all platforms. The workflow runs on `workflow_dispatch` and `v*` tags;
use the GitHub Actions **Run workflow** action to build without creating a tag.
Artifacts are uploaded separately by platform.

Requirements for native packaging: Inno Setup 6 on Windows, `hdiutil` on
macOS, `dpkg-deb` and `appimagetool` on Linux. If a tool is missing the script
skips that artifact and still produces the portable archive.

## Project layout

```text
nxsheet/                     application source
├── main.py                  entry point
├── main_window.py           main window, docks, printing, language switching
├── menus.py                 menu bar, context menus, language menu
├── actions.py               all QActions
├── workflows.py             file, edit, import/export, printing workflows
├── autosave.py              auto save, automatic backups, version history
├── i18n.py                  nine language translation catalog
├── settings.py              persisted application settings
├── templates.py             business templates
├── dialogs.py               file, find, chart, print, about dialogs
├── grid.py / grid_renderer.py   the spreadsheet widget and renderer
├── model/model.py           code array, cell attributes, evaluation
├── lib/excel_functions.py   107 spreadsheet functions
├── interfaces/pys.py        native workbook reader and writer
├── interfaces/xlsx.py       XLSX import
├── ai/engine.py             local AI and document support
└── share/                   icons, examples, manual, tutorial
installers/                  PyInstaller spec, Inno Setup, DMG, AppImage, deb, MIME
build_installers.py          builds all platform installers
docs/                        user guide, feature audit, file format
```

## Documentation

* [docs/GUIDE.md](docs/GUIDE.md) — complete user guide
* [docs/FEATURES.md](docs/FEATURES.md) — verified feature status, including
  the features that are **not** implemented
* [docs/FILE_FORMAT.md](docs/FILE_FORMAT.md) — the `.nix` workbook format
* `nxsheet/share/doc/manual` and `nxsheet/share/doc/tutorial` — in-app help
  (`Help → Manual`, `Help → Tutorial`)
* Help → About shows version, platform, license, languages and support

## Feature status

Nexuzy Sheet 1.2.0 implements workbook and file management, cell editing,
formatting, the formula engine, sorting, importing/exporting, printing,
templates, charts, macros, auto save, backups and nine languages.

It is **not** a complete Excel clone. The following are not implemented in
this release and are listed with full detail in
[docs/FEATURES.md](docs/FEATURES.md): pivot tables, conditional formatting,
filtering, data validation, named ranges, comment threads, hyperlinks,
real-time collaboration, cloud sync, accounts and 2FA, password-protected
workbooks, a plugin system and a web/mobile build.

## License

Nexuzy Sheet is released under the **MIT License**. It is free and open source
and stays free to use forever.

Copyright (c) 2026 Nexuzy Lab. See [LICENSE](LICENSE) for the full text.
The optional local AI model download is a separate runtime component and is
subject to the upstream model license.

### Legal documents

* [LICENSE](LICENSE) — MIT licence of the Nexuzy Sheet source code
* [docs/EULA.md](docs/EULA.md) — end user licence agreement
* [docs/TERMS_OF_SERVICE.md](docs/TERMS_OF_SERVICE.md) — terms of service
* [docs/PRIVACY_POLICY.md](docs/PRIVACY_POLICY.md) — privacy policy (no
  telemetry, no account, local AI)
* [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) — licences of the bundled
  Qt, PyQt6, llama.cpp, Qwen model and Python dependencies, with compliance
  notes

In the application, the same documents are available from **Help → About**
(tabs *License*, *EULA*, *Terms* and *Privacy*).

## Support

* Website: <https://nexuzy.in>
* Company: **Nexuzy Lab**
* Support e-mail: <support@nexuzy.in>
* Information e-mail: <info@nexuzy.in>
* Developers: David and Manoj Konar
* Web app: <https://sheet.nexuzy.in>
* GitHub: <https://github.com/david0154/nexuzy_sheet>
