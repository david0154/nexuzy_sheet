# Nexuzy Sheet AI Integration

Lightweight, local AI for spreadsheet operations. Nexuzy Sheet is a desktop
spreadsheet application developed and published by Nexuzy Lab. The desktop
app's supported offline assistant is implemented in `nxsheet/ai/engine.py`
with Qwen2.5-0.5B-Instruct GGUF through `ctransformers`; it creates structured
formula/table actions and receives limited nearby workbook context. It does
not execute generated Python. The current app links are
<https://sheet.nexuzy.in> and <https://github.com/david0154/nexuzy_sheet>.

This directory contains an experimental integration layer, not the runtime
used by the shipped desktop AI panel. Its OCR and coordinator examples are not
wired into the desktop prompt flow; do not infer that they are included in the
installer or available as working app features.

## Overview

Nexuzy Sheet AI consists of four focused components:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Brain** | Qwen2.5-0.5B-Instruct (GGUF Q4 + llama.cpp) | Understand commands, generate formulas, lightweight reasoning |
| **OCR** | PaddleOCR PP-OCRv6 Tiny | Read text/numbers from images and documents |
| **Image Prep** | OpenCV | Deskew, denoise, crop, perspective correction |
| **PDF Reading** | PyMuPDF | Extract text/images/pages from PDFs |

**No cloud APIs. Model inference is local. Qwen model weights must be
explicitly downloaded by the user; no AI model is bundled in the installer.**

---

## Installation

### 1. Install AI Dependencies

```bash
pip install -r nxsheet/optional_ai_requirements.txt
```

### 2. Download Qwen2.5-0.5B-Instruct Model

The model (512 MB GGUF Q4 quantized) must be downloaded once:

```python
from pyspread.ai_integration import AICoordinator

coordinator = AICoordinator()
# TODO: Implement model download functionality
# coordinator.download_model("qwen2.5-0.5b-instruct")
```

For now, download manually from:
- Hugging Face: `qwen/Qwen2.5-0.5B-Instruct-GGUF`
- Modelscope: Qwen2.5-0.5B-Instruct

Place in `~/.nexuzy_sheet/ai_models/qwen2.5-0.5b-instruct.gguf`

### 3. First-Run Initialization

When you first use AI features, Nexuzy Sheet automatically:
1. Checks dependencies
2. Downloads OCR models (PaddleOCR)
3. Initializes all components
4. Creates cache directory

---

## API Usage

### Basic Command Processing

```python
from pyspread.ai_integration import AICoordinator

coordinator = AICoordinator()
coordinator.initialize_async()  # First time only

# User asks AI
action = coordinator.process_command(
    "Add GST of 18% to B5",
    context={"current_cell": "B5", "column_headers": ["Item", "Price", "Total"]}
)

print(action.to_dict())
# Output:
# {
#     "action": "formula",
#     "payload": {"cell": "E5", "formula": "=B5*1.18"},
#     "explanation": "Multiplies B5 by 1.18 to add 18% GST",
#     "confidence": 0.92
# }
```

### Formula Explanation

```python
explanation = coordinator.explain_formula("=SUM(A1:A10)/COUNT(A1:A10)")
print(explanation)
# Output: "This formula calculates the average of cells A1 to A10..."
```

### Import from Image

```python
action = coordinator.import_from_image("/path/to/invoice.jpg", output_cell="A1")
# Returns ImportTableAction with extracted table data
```

### Import from PDF

```python
# Text PDF
action = coordinator.import_from_pdf("/path/to/document.pdf", page=0)

# Scanned PDF (uses OCR automatically)
action = coordinator.import_from_pdf("/path/to/scanned.pdf", page=0)
```

---

## Supported AI Actions

All AI responses are structured JSON (validated):

### 1. Generate Formula

```json
{
  "action": "formula",
  "payload": {"cell": "E5", "formula": "=C5*D5"},
  "explanation": "Multiplies quantity by price",
  "confidence": 0.95
}
```

### 2. Explain Formula

```json
{
  "action": "explain_formula",
  "payload": {"cell": "E5"},
  "explanation": "This formula multiplies the quantity in C5 by the price in D5...",
  "confidence": 0.98
}
```

### 3. Find/Search

```json
{
  "action": "find",
  "payload": {"query": "Kolkata", "search_columns": [0, 1]},
  "explanation": "Searching for 'Kolkata' in columns A-B",
  "confidence": 0.9
}
```

### 4. Data Analysis

```json
{
  "action": "data_analysis",
  "payload": {"analysis_type": "highest_sales", "result": "Product B"},
  "explanation": "Product B has the highest total sales (₹45,000)",
  "confidence": 0.88
}
```

### 5. Format Cells

```json
{
  "action": "format",
  "payload": {"cells": ["A1:B5"], "format": {"bold": true, "background": "#FFFF00"}},
  "explanation": "Making headers bold and yellow",
  "confidence": 0.92
}
```

### 6. Detect Duplicates

```json
{
  "action": "detect_duplicates",
  "payload": {"key_columns": [0, 1]},
  "explanation": "Checking for duplicate rows based on columns A and B",
  "confidence": 0.85
}
```

### 7. Import Table

```json
{
  "action": "import_table",
  "payload": {
    "data": [
      ["Item", "Qty", "Price"],
      ["Keyboard", "2", "800"],
      ["Mouse", "1", "500"]
    ],
    "start_cell": "A1"
  },
  "explanation": "Imported table from image (3 rows × 3 columns)",
  "confidence": 0.82
}
```

### 8. Error

```json
{
  "action": "error",
  "payload": {"error": "Could not understand", "suggestion": "Try: 'Add 18% to B5'"},
  "explanation": "Could not understand your request",
  "confidence": 0.0
}
```

---

## Integration with Nexuzy Sheet

### UI Components

**AI Prompt Panel** (in sidebar):
```
┌─────────────────────────┐
│ ✨ Ask Nexuzy AI        │
│                         │
│ [Ask anything...]     →│
│                         │
│ Action: formula         │
│ Explanation: ...        │
│ Confidence: 95%         │
│                         │
│ [📷 Import] [📄 PDF]   │
└─────────────────────────┘
```

**Toolbar Button**: ✨ AI button in main toolbar

**Right-Click Menu**: "Ask AI" option in cell context menu

### Implementation in Main Window

```python
from pyspread.ai_integration import AICoordinator, AIPanelWidget

class MainWindow:
    def __init__(self):
        # Initialize AI
        self.ai_coordinator = AICoordinator()
        
        # Add AI panel to sidebar
        self.ai_panel = AIPanelWidget(coordinator=self.ai_coordinator)
        self.sidebar.addWidget(self.ai_panel)
        
        # Connect AI action signal
        self.ai_panel.action_received.connect(self.on_ai_action)
    
    def on_ai_action(self, action):
        """Execute AI-generated action in spreadsheet"""
        if action.action == AIActionType.FORMULA:
            cell = action.payload["cell"]
            formula = action.payload["formula"]
            self.set_cell_formula(cell, formula)
        
        elif action.action == AIActionType.FIND:
            query = action.payload["query"]
            self.find_and_select(query)
        
        # ... handle other action types
```

---

## System Prompt

The Qwen2.5-0.5B-Instruct model operates under this system prompt (constrains output):

```
You are Nexuzy Sheet AI, an assistant for spreadsheet operations.
Your role is to help users by generating formulas, explaining spreadsheet 
operations, and analyzing data.

IMPORTANT: Always respond with valid JSON action format.
Never generate arbitrary Python code.
Only generate valid spreadsheet formulas starting with =
Keep explanations clear and concise.
```

---

## Performance

| Component | Time | Memory |
|-----------|------|--------|
| Qwen2.5-0.5B-Instruct | 1-3s per command | ~490 MB |
| PaddleOCR | 0.5-2s per image | ~500 MB |
| OpenCV preprocessing | 100-500ms | ~100 MB |
| PyMuPDF | 50-200ms per page | ~50 MB |

**Total startup**: ~2 seconds (after first-run initialization)

---

## Troubleshooting

### AI not initializing

```
Error: OpenCV is not installed
Solution: pip install opencv-python
```

### Model not found

```
Error: Model not found: ~/.nexuzy_sheet/ai_models/qwen2.5-0.5b-instruct.gguf
Solution: Download from Hugging Face and place in that directory
```

### OCR not working

```
Error: PaddleOCR not available
Solution: pip install paddleocr
```

### Slow inference

- Reduce context window: `QwenInterface(model_path, n_ctx=1024)`
- Increase threads: `QwenInterface(model_path, n_threads=8)`
- Lower temperature for faster deterministic responses

---

## Architecture Diagram

```
┌────────────────────────────────────────────┐
│          NEXUZY SHEET (Main App)           │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────┐    │
│  │   AI Coordinator (Central Hub)   │    │
│  └──────────────────────────────────┘    │
│                 ↓                         │
│    ┌────┬────────┬────────┬──────┐      │
│    ↓    ↓        ↓        ↓      ↓      │
│  Qwen  OCR   OpenCV   PyMuPDF  Config  │
│  (LLM) (Text) (Prep)   (PDF)           │
│                                            │
│  → All run locally, offline              │
│  → No cloud APIs                         │
│  → No large models                       │
│                                            │
└────────────────────────────────────────────┘
```

---

## Dependencies Summary

```toml
[ai-dependencies]
llama-cpp-python = ">=0.2.0"      # Qwen2.5 inference
paddleocr = ">=2.8.0"             # PP-OCRv6 Tiny
opencv-python = ">=4.8.0"         # Image preprocessing
pymupdf = ">=1.23.0"              # PDF handling
numpy = ">=1.24.0"                # Numerical operations
```

---

## License

Same as Nexuzy Sheet: MIT License

---

**Nexuzy Sheet AI: Lightweight. Local. Powerful.**
