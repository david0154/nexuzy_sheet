# NXSheet Templates & AI PDF Extraction Guide

## 📋 Available Pre-Built Templates

NXSheet includes 5 professional templates with complete design and styling:

### 1. **Invoice** 📄
- Professional invoice template with itemized billing
- Fields: Invoice #, Date, Bill To, Due Date, Items, Amounts, GST calculation
- Includes formulas for tax and total calculations
- Styling: Currency formatting, centered alignment

### 2. **Attendance Register** 📅
- Employee attendance tracking by date
- Monthly attendance sheet with 31 date columns
- Automatic present-day counter
- Fields: Employee ID, Name, Daily attendance status (P/A)

### 3. **General Ledger** 📊
- Financial transaction ledger with debit/credit columns
- Account tracking with running balance
- Fields: Date, Reference, Description, Debit, Credit, Balance
- Includes SUM formulas for totals

### 4. **Payroll Sheet** 💰
- Employee salary calculation with deductions
- Fields: Basic, HRA, DA, Gross, Income Tax, Provident Fund, Net Salary
- Automatic calculation formulas for taxes and deductions
- Multi-employee support with totals row

### 5. **Budget Planning** 📈
- Budget vs Actual expense tracking
- Variance and percentage variance calculation
- Fields: Category, Budgeted Amount, Actual Spent, Variance, % Variance
- Automatic variance calculations

---

## 🎨 How to Use Templates in the GUI

### Method 1: Load Template Directly
1. Open NXSheet application
2. Click the **"Ask Nexuzy AI"** dock panel on the right
3. In the **"Templates"** section at the top, select a template from the dropdown:
   - "Invoice"
   - "Attendance Register"
   - "General Ledger"
   - "Payroll Sheet"
   - "Budget Planning"
4. Click **"Load Template"** button
5. The template with sample data is loaded into your spreadsheet at cell A1

### Method 2: Extract PDF and Auto-Populate Template
1. Have a PDF invoice or bill ready
2. Click the **"📄 Invoice"** button in the AI panel
3. Select your PDF file
4. NXSheet will:
   - Extract data from the PDF (invoice number, date, items, amounts)
   - Auto-populate the Invoice template
   - Maintain the professional template design
   - Apply formulas for calculations

---

## 🤖 AI PDF Extraction Features

### How It Works

When you upload a PDF invoice/bill:

1. **Text Extraction**: PyMuPDF or OCR extracts text from PDF
2. **Data Parsing**: AI identifies key fields:
   - Invoice Number
   - Invoice Date
   - Total Amount
   - Vendor/Company Name
   - Customer Name
   - Line Items (Description, Qty, Price)
3. **Template Population**: Data is inserted into the Invoice template:
   - Maintains professional formatting
   - Applies formulas for GST/tax calculations
   - Preserves column alignment and styling

### Supported Document Types
- ✅ PDF invoices and bills
- ✅ JPEG/PNG images of invoices
- ✅ Any scanned business document

### Example Workflow

```
PDF File (invoice.pdf)
    ↓
AI Text Extraction
    ↓
Parse structured data
    ↓
Load Invoice Template
    ↓
Populate with extracted data
    ↓
Professional spreadsheet with same style/design as PDF
```

---

## 📝 Template Styling & Formatting

Each template includes:

### Invoice Template Styling
```
Font Size: 12pt
Title Row: Bold, centered
Header Row: Bold background
Currency Columns: 2-decimal formatting
Centered Columns: Item Qty alignment
Formulas: Auto-calculation of tax and total
```

### Attendance Template Styling
```
Font Size: 10pt
All Date Columns: Centered
Employee ID: Left-aligned
Auto-Count: COUNTIF formula for present days
```

### Ledger Template Styling
```
Font Size: 11pt
Date Column: Date formatting
Currency Columns: 2-decimal formatting
Balance Column: Running total formula
```

### Payroll Template Styling
```
Font Size: 11pt
All Salary Columns: Currency formatting
Tax Formulas: Auto-calculation (10% IT, 12% PF)
Net Salary: Automatic deduction calculation
Total Row: SUM formulas
```

### Budget Template Styling
```
Font Size: 11pt
Amount Columns: Currency formatting
% Variance Column: Percentage formatting
Auto-calculation: Variance = Actual - Budget
```

---

## 🔧 Using Templates Programmatically

If you're using NXSheet as a library:

```python
from nxsheet.ai.engine import NexuzyAIController
from nxsheet.templates import TemplateManager

# Initialize AI controller
controller = NexuzyAIController('./models')

# Load a template
action = controller.load_template('invoice')
print(action.data)  # Returns 2D array with template structure

# Extract PDF and populate template
action = controller.handle_pdf_with_template('invoice.pdf', template_name='invoice')
print(action.data)  # Returns template populated with extracted data

# Get list of available templates
templates = controller.get_available_templates()
# Returns: {'invoice': 'Invoice', 'attendance': 'Attendance Register', ...}
```

---

## 📌 Advanced Template Features

### Styling Configuration
Each template includes a `styling` dictionary:

```python
{
    "title_row": 0,              # Row index for title
    "header_row": 5,             # Row index for headers
    "data_start_row": 6,         # Where data rows begin
    "font_size": 12,             # Default font size
    "currency_columns": [2, 4],  # Columns with currency formatting
    "centered_columns": [1, 3],  # Columns with center alignment
    "percentage_columns": [4],   # Columns with % formatting
    "bold_rows": [7],            # Rows to make bold
    "date_columns": [0],         # Columns with date formatting
}
```

### Custom Data Insertion
You can load a template with custom data:

```python
custom_data = [
    ["Consulting Services", 5, 2000, 18, "=C7*(1+D7/100)"],
    ["Support Hours", 10, 500, 18, "=C8*B8*(1+D8/100)"],
]
action = controller.load_template('invoice', data=custom_data)
```

---

## 🚀 Quick Start

1. **Open the app**: `python main.py`
2. **Click AI panel**: Right sidebar "Ask Nexuzy AI"
3. **Load template**: Choose from dropdown → "Load Template"
4. **Or extract PDF**: Click "📄 Invoice" → select PDF → auto-populate
5. **Edit and save**: Modify template data as needed

---

## 📚 Template Formulas Reference

### Invoice
- `=B5*1.18` - Add 18% GST to amount
- `=SUM(E7:E9)` - Total all line items

### Attendance
- `=COUNTIF(C5:AG5,"P")` - Count present days

### Ledger
- `=D5+D6` - Running balance calculation
- `=SUM(D6:D9)` - Total debits

### Payroll
- `=C5+D5+E5` - Gross salary
- `=F5*0.10` - Income tax (10%)
- `=F5*0.12` - Provident Fund (12%)
- `=F5-G5-H5` - Net salary

### Budget
- `=C5-B5` - Variance (Actual - Budget)
- `=D5/B5*100` - Variance %

---

## 💡 Tips & Tricks

- **Batch Import**: Load a template once, then use it as a base for multiple documents
- **PDF Merge**: Extract multiple invoice PDFs and stack them using the same template
- **Custom Calculations**: Edit template formulas to match your specific business rules
- **Save as Template**: After customizing, save your modified template for future use

---

## ❓ Troubleshooting

**Problem**: Template loads but PDF data doesn't extract  
**Solution**: Make sure PDF has readable text (not just image). Try OCR if needed: `pip install paddleocr`

**Problem**: Currency not formatting correctly  
**Solution**: Ensure numeric values are entered (not text). Use formulas for calculations.

**Problem**: Formulas not calculating  
**Solution**: Check that cell references are correct. Templates use absolute references (A1, not $A$1) for flexibility.

---

**Questions?** Check the AI panel output for detailed explanations after loading templates or extracting PDFs!
