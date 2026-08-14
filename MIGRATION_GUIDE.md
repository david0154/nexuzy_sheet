# NXSheet Application - Migration Complete ✅

## Project Rename: pyspread → nxsheet

The entire pyspread project has been rebranded to **nxsheet** (Nexuzy Sheet). This includes:

### ✅ Completed Changes

1. **Folder Rename**
   - `pyspread/` → `nxsheet/`
   - All internal package structure updated

2. **Code Updates**
   - 28 Python files updated with new imports
   - Changed: `from pyspread.*` → `from nxsheet.*`
   - Changed: `import pyspread.*` → `import nxsheet.*`

3. **Requirements Management**
   - **Primary requirements file**: `nxsheet/requirements.txt`
   - **Root requirements.txt**: Contains optional/extra dependencies
   - Removed `llama-cpp-python` from mandatory dependencies (Windows long-path issue)
   - Note: Install llama-cpp-python manually if needed:
     ```bash
     pip install --no-build-isolation llama-cpp-python
     ```

4. **Configuration Files**
   - Updated desktop files (nxsheet.desktop, nxsheet.pth)
   - Updated setup files (setup.py, pyproject.toml)
   - Updated CLI references

---

## ✨ New Features: Invoice/Bill Upload

### Added Invoice Processing
The AI layer now supports converting bills, invoices, and receipts into spreadsheet format.

#### New Components
1. **InvoiceProcessor** - Extract structured invoice data
2. **on_ai_import_invoice()** - UI handler for invoice uploads
3. **handle_invoice_upload()** - AI controller method for processing

#### UI Changes
The Ask NXSheet AI panel now includes 3 upload buttons:
- 📄 **Invoice** - Convert bills/invoices to spreadsheet
- 🖼️ **Image** - Extract table data from images
- 📕 **PDF** - Extract content from PDFs

#### Supported Formats
- PDF invoices (`*.pdf`)
- Image invoices (`*.jpg`, `*.jpeg`, `*.png`, `*.bmp`)

#### How to Use
1. Click the **Invoice** button in the AI dock
2. Select a bill/invoice file (PDF or image)
3. The AI extracts:
   - Invoice number
   - Date
   - Customer/Vendor details
   - Line items (description, quantity, price)
   - Total amount
4. Data is automatically inserted into the spreadsheet at cell A1

---

## 🚀 Running the Application

### CLI
```bash
python -m nxsheet
python -m nxsheet --help
python -m nxsheet path/to/file.nxs
```

### Module Import
```python
from nxsheet.main_window import MainWindow
from nxsheet.ai.engine import NexuzyAIController
```

### Tests
```bash
# Run all AI engine tests
python -m pytest nxsheet/test/test_ai_engine.py -v

# Run specific test
python -m pytest nxsheet/test/test_ai_engine.py::test_ai_controller_generates_formula_action -v
```

---

## 📦 Dependencies

### Mandatory (in nxsheet/requirements.txt)
- PyQt6 (>=6.4) - GUI framework
- numpy (>=1.1)
- setuptools (>=40.0)
- markdown2 (>= 2.3)
- opencv-python (>=4.8.0) - Image processing
- paddleocr (>=2.8.0) - OCR for text extraction
- pymupdf (>=1.23.0) - PDF processing

### Optional (in root requirements.txt)
- matplotlib - Charting
- pyenchant - Spell checking
- rpy2 - R integration
- plotnine - Advanced plotting
- pycel - Excel compatibility
- openpyxl - Excel file handling

### Note on llama-cpp-python
Removed from mandatory requirements due to Windows long-path limitations during installation.
**Manual installation** (if needed):
```bash
pip install --no-build-isolation llama-cpp-python
# or use prebuilt wheels if available for your platform
```

---

## 🧪 Test Results

All tests pass successfully:
```
nxsheet/test/test_ai_engine.py::test_ai_controller_generates_formula_action PASSED
nxsheet/test/test_ai_engine.py::test_main_window_has_ai_dock PASSED
nxsheet/test/test_ai_engine.py::test_ai_dependency_requirements_include_local_stack PASSED
nxsheet/test/test_ai_engine.py::test_grid_data_changed_is_safe_when_main_window_is_deleted PASSED

4 passed in 1.08s
```

---

## 📁 Directory Structure

```
nxsheet/
├── __init__.py           # APP_NAME = "Nexuzy Sheet"
├── __main__.py          # Entry point
├── main.py              # Application launcher
├── main_window.py       # Main UI with AI dock panel
├── ai/
│   ├── __init__.py
│   └── engine.py        # AI controller + Invoice processor
├── model/
├── lib/
├── interfaces/
└── test/
    └── test_ai_engine.py    # AI tests
```

---

## 🔧 Key AI Features

### 1. Text-based Commands
```python
action = controller.handle_text_request("Add GST of 18% to B5")
# Returns: formula action with "=B5*1.18"
```

### 2. Image Processing
```python
data = controller.handle_image_request("path/to/invoice.jpg")
# Returns: OCR-extracted text with bounding boxes
```

### 3. Invoice Upload (NEW)
```python
action = controller.handle_invoice_upload("path/to/invoice.pdf")
# Returns: import_table action with structured invoice data
```

### 4. PDF Processing
```python
data = controller.handle_pdf_request("path/to/document.pdf")
# Returns: page-by-page extraction
```

---

## ⚠️ Known Issues & Workarounds

### Windows Long Path Support
- **Issue**: `llama-cpp-python` installation fails on Windows without long path support
- **Solution**: 
  - Enable Windows Long Path support (see pip warning for details)
  - Or install with: `pip install --no-build-isolation llama-cpp-python`
  - Or use a Python distribution with prebuilt wheels

### Import Errors
- If you see "No module named 'pyspread'", ensure:
  - PYTHONPATH includes the nxsheet parent directory
  - You're using `nxsheet` imports, not `pyspread`

---

## 📝 Migration Notes

If you have existing code that imports from pyspread:
- Change: `from pyspread.xxx import yyy`
- To: `from nxsheet.xxx import yyy`

All file paths and configurations have been updated automatically.

---

**Version**: 1.0.0  
**App Name**: Nexuzy Sheet  
**Status**: Ready for Development  
**Last Updated**: 2026-08-14
