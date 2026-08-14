# Nexuzy Sheet

Nexuzy Sheet is a Python spreadsheet workspace for business data, templates, calculations, exports, and local AI-assisted workflows.

## Overview

- Spreadsheet editing for business and finance workflows
- Built-in templates for invoice, attendance, ledger, payroll, and budget sheets
- CSV, XLSX, XLS, ODS, SVG, and PDF export support
- Local AI assistant panel with optional document and image imports
- Python-only default install path without C++ build toolchain requirements

## Features

- Multi-sheet spreadsheet interface
- Formula-based calculations
- Cell formatting, merge support, and style controls
- Business document templates
- PDF/image upload workflows
- Local fallback AI engine for formulas and actions
- Export and print support for spreadsheet areas

## Install

### 1) Clone the repository

```bash
git https://github.com/david0154/nexuzy-sheet.git
cd <your-repo>
```

### 2) Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install the app dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Optional AI/OCR extras:

```bash
python -m pip install -r nxsheet/optional_ai_requirements.txt
```

## First Run and AI Model Download

On first launch, the app checks for the default local AI model and downloads it automatically into the user data folder:

```text
~/.nexuzy_sheet/models/
```

The built-in AI path is intentionally offline-safe:

- It does not force a C++ build toolchain
- It does not require llama-cpp-python by default
- If the model is unavailable or the network is not reachable, the app falls back to its built-in spreadsheet action engine without crashing

## Run the app

```bash
python -m nxsheet
```

## Project structure

- `nxsheet/` - application source code
- `nxsheet/templates.py` - business templates
- `nxsheet/ai/engine.py` - local AI and document logic
- `requirements.txt` - base Python app requirements
- `nxsheet/optional_ai_requirements.txt` - optional AI/OCR requirements

## License

This project is released under the GNU General Public License v3. See [LICENSE](LICENSE) for the full text.

The optional AI model download is a separate runtime component and is subject to the upstream model provider license. The app itself remains under GPL v3.

## Support

- GitHub repository: add your repository URL here
- Project website: https://nexuzy.in
- Email: support@nexuzy.in
