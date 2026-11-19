# Nexuzy Sheet user guide

This guide covers daily work with Nexuzy Sheet 1.5.0 on Windows, macOS and
Linux. For the exact implementation status of every feature see
[FEATURES.md](FEATURES.md); for the workbook format see
[FILE_FORMAT.md](FILE_FORMAT.md).

## 1. Installation and first start

1. Download the installer of your platform:
   * Windows: `Nexuzy-Sheet-<version>-windows-x64-setup.exe`
   * macOS: `Nexuzy-Sheet-<version>-macos.dmg`
   * Linux: `.AppImage`, `.deb` or `.tar.gz`
2. Install or unpack it and start **Nexuzy Sheet**.
3. The first start creates the user folder `~/.nexuzy_sheet`. It holds the
   auto save area, the backups and (if used) the local AI model.

Starting from source:

```bash
python -m pip install -r requirements.txt
python -m nxsheet
```

An existing workbook can be opened from the command line:

```bash
python -m nxsheet "C:/Work/Report.nix"
```

## 2. The workspace

| Area | Purpose |
| --- | --- |
| Menu bar | File, Edit, View, Format, Macro, Help |
| Main toolbar | New, open, save, print, edit and formatting shortcuts |
| Entry line | Formula/value editor of the current cell (`S[row, column, table]`) |
| Grid | The spreadsheet itself; four synchronised views are available |
| Table tabs | Worksheets of the workbook (called *tables*) |
| Macro panel | Python scripts that belong to the workbook |
| AI panel | Optional local assistant; the app works without it |
| Status bar | Selection statistics, zoom, safe mode, auto save messages |

## 3. Workbooks, sheets and files

### New workbook

`File → New` asks for a grid shape (rows, columns, tables). The default
`1000 × 100 × 3` is fine for most work. The maximum is `1000000 × 100000 ×
100`.

### Worksheets

Every workbook contains one or more tables. A cell address is
`S[row, column, table]`, for example `S[4, 2, 1]` for row 4, column 2 of the
second table. Switch tables with the tabs under the grid, add one with
`Edit → Insert table` and remove one with `Edit → Delete table`.

### Saving: the `.nix` format

`.nix` is the native Nexuzy Sheet workbook format and is offered first in the
save dialog. It stores the cell code, formatting, row heights, column widths,
macros, images and charts, compressed with bzip2.

* `Ctrl+S` saves to the current path.
* `Shift+Ctrl+S` saves a copy under a new name.
* `.nxl` (uncompressed) and `.nxs` (compressed) are still readable and can be
  saved for compatibility with older builds.

### Auto save and automatic backups

Auto save is enabled by default (`File → Auto save`):

* While the workbook has unsaved changes, Nexuzy Sheet writes a recovery copy
  every 120 seconds to `~/.nexuzy_sheet/autosave`.
* After every successful save it copies the workbook to
  `~/.nexuzy_sheet/backups/<workbook name>` and keeps the newest 20 versions.
* On exit a final recovery copy is written when changes are unsaved.

`File → Version history…` lists recovery copies and backups with their
timestamp and size. Select an entry and press **Restore** to open it. Delete
removes a version permanently.

### Recent files

`File → Recent files` shows the five most recently opened workbooks.

### Import and export

`File → Import` reads CSV/TSV data with delimiter and encoding detection and
writes it into the current grid. `File → Open` also reads `.xlsx` workbooks
when `openpyxl` is installed.

`File → Export` writes the selection or the defined area as CSV, JSON, PDF,
TXT, HTML, XLSX, XLS, ODS or SVG, plus PNG/JPG for image and chart cells.

## 4. Entering and editing data

* Click a cell and type into the entry line. `Enter` confirms and moves down.
* Drag or `Shift`-click to select a rectangle; typing then fills the whole
  selection row by row.
* `Ins` toggles selection mode, which inserts cell references into the entry
  line instead of editing.
* `Ctrl+C` copies the code of the cells, `Shift+Ctrl+C` copies their displayed
  results. `Ctrl+V` pastes from the clipboard.
* `Ctrl+Z` undoes, `Shift+Ctrl+Z` redoes.
* `Edit → Fill down` (`Ctrl+Shift+D`) and `Fill right` (`Ctrl+Shift+R`) copy
  the first cell of a selection across it.
* `Edit → Find…` (`Ctrl+F`), `F3` for the next match, `Shift+Ctrl+F` to
  replace.
* `View → Go to cell` jumps to a row/column/table address.

Rows and columns are inserted, deleted and resized from the `Edit` menu, the
context menus of the headers and by dragging header borders.

## 5. Formulas

Cells contain Python expressions. Spreadsheet functions accept cell ranges:

```python
SUM(S[0:10, 2, 0])                     # numbers in column 2, rows 0-9
AVERAGE(S[1:5, 2, 0])
IF(S[0, 0, 0] > 100, "high", "low")
VLOOKUP("Apple", S[0:20, 0:2, 0], 2, False)
TEXT(S[0, 1, 0], "#,##0.00")
PMT(0.05/12, 60, -10000)
```

`Shift+F3` or `Macro → Insert function…` opens the searchable function
catalog with signatures. Any Python expression is allowed, so `numpy`,
`math` and functions defined in the macro panel can be used as well.

Ranges use Python slice syntax with three axes: rows, columns, tables. A
single cell is `S[row, column, table]`; `S[:, :, 1]` is a whole table.

## 6. Formatting

The Format toolbar and `Format` menu provide fonts, size, bold, italic,
underline, strikethrough, text colour, background colour, borders (per side
and outline, eight widths), horizontal and vertical alignment, text rotation,
rendering as text/image/markup, merged cells, frozen and locked cells and
button cells.

* `Format → Copy format` / `Paste format` and `Clone formatting` work as a
  format painter.
* `Format → Default format` clears formatting of the selection.
* `Format → AutoFit columns` widens the selected columns until the longest
  value fits; `AutoFit rows` grows the selected rows to the wrapped text
  height; `AutoFit selection` does both for the current selection. The same
  actions are in the header context menus.
* `View → Dark mode` switches between the light and dark theme.

## 7. Sorting and data work

`Edit → Sort ascending` / `Sort descending` sorts the selected rows by the
current column. For heavier data work use Python directly in a cell or in the
macro panel, e.g. `sorted(...)`, `numpy` aggregations or a custom function.
Filtering, pivot tables and conditional formatting are not part of 1.3.0 (see
[FEATURES.md](FEATURES.md)).

## 8. Charts and images

* `Macro → Insert chart…` embeds a matplotlib chart. The chart is Python code
  and updates when the source cells change.
* `Macro → Insert image…` places an image or SVG into the selected cell.
* Chart cells export as SVG/PNG through `File → Export`.

## 9. Printing and PDF

1. `File → Print preview` shows the layout; `File → Print` prints.
2. `Print area` limits output to a cell range.
3. The native print dialog of your platform sets printer, paper, orientation
   and margins.
4. Printing or previewing to a PDF printer produces a PDF; `File → Export →
   PDF` is the direct route.

## 10. Macros and automation

The macro panel stores Python code inside the workbook (`.nix`). Code placed
there runs in the application namespace, so functions defined there are
available in every cell:

```python
def margin(revenue, cost):
    """Gross margin in percent"""
    return (revenue - cost) / revenue * 100
```

Then use `=margin(S[0,0,0], S[0,1,0])` in a cell. Because cells are Python,
batch processing, report generation and custom functions are written in the
same language. See [FEATURES.md](FEATURES.md) for the automation features that
are not implemented.

### AI tools and optional offline model

The AI panel uses the optional offline Qwen2.5-0.5B-Instruct model (GGUF Q4_K_M)
to interpret spreadsheet prompts. It receives a limited snapshot around the
active cell and can produce supported spreadsheet actions such as formulas or
an importable table. Generated tables can receive title/header styling. Model
loading and inference run in the background when a prompt is submitted.

Open **Help → Offline AI model** and choose **Download now**. The setup runs in
a background worker; progress appears in the status bar. A valid model in
`~/.nexuzy_sheet/models/` is reused, and the llama.cpp CPU runtime (about
25 MB) is installed once next to it. The roughly 490 MB model weights are not
bundled and no download starts automatically.

The assistant is called **Nexuzy AI** and is informed about the application it
lives in: product name and version, company and publisher (Nexuzy Lab),
developers, the official web app at <https://sheet.nexuzy.in>, the website and
source repository, support address, and the workbook formats it opens. Every
prompt also carries the complete built-in formula library — all 107 functions
with their signatures (and full descriptions for the functions named in your
request), so it can pick a supported function, explain what a function does, and
avoid inventing functions that do not exist. Formulas can be described in the
same panel: ask “what does VLOOKUP do?” and the answer appears as text.

Nexuzy AI is a small model and can make mistakes; review formulas and generated
cell content before relying on them. Inference is local and does not require an
API key.

## 11. Preferences, theme and language

`File → Preferences…` changes the cell timeout, refresh interval, status bar
statistics and other application settings. The theme is switched in
`View → Dark mode`.

### Languages

`View → Language` switches the interface language immediately:

| Code | Language |
| --- | --- |
| `en` | English |
| `hi` | हिन्दी (Hindi) |
| `bn` | বাংলা (Bengali) |
| `ta` | தமிழ் (Tamil) |
| `es` | Español (Spanish) |
| `fr` | Français (French) |
| `zh` | 中文 (Chinese) |
| `ru` | Русский (Russian) |
| `ja` | 日本語 (Japanese) |

The choice is stored in the application settings and restored on the next
start. The translation catalog covers menus, the common actions and the About
dialog (`nxsheet/i18n.py`). Strings that are not in the catalog stay in
English; adding a language means adding one dictionary there.

## 12. Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| `Ctrl+N` | New workbook |
| `Ctrl+S` | Save |
| `Shift+Ctrl+S` | Save as |
| `Ctrl+P` | Print |
| `Ctrl+Q` | Quit |
| `Ctrl+Z` / `Shift+Ctrl+Z` | Undo / Redo |
| `Ctrl+X` / `Ctrl+C` / `Ctrl+V` | Cut / Copy / Paste |
| `Shift+Ctrl+C` | Copy results |
| `Shift+Ctrl+V` | Paste as… |
| `Ctrl+F` / `F3` / `Shift+Ctrl+F` | Find / Find next / Replace |
| `Ctrl+Shift+D` / `Ctrl+Shift+R` | Fill down / Fill right |
| `Ins` | Selection mode |
| `Shift+F3` | Insert function |
| `F11` | Full screen |

## 13. Data safety checklist

1. Keep `File → Auto save` enabled.
2. Save with `Ctrl+S`; every save creates a version in
   `~/.nexuzy_sheet/backups`.
3. After a crash, start the app and use `File → Version history…` to restore
   the recovery copy.
4. Workbooks are compressed, **not encrypted**. Store sensitive workbooks in
   an encrypted folder or volume.

## 14. Troubleshooting

| Symptom | Fix |
| --- | --- |
| `.xlsx` cannot be opened | Install the optional dependency: `python -m pip install openpyxl` |
| PDF export fails | Check that a PDF printer is available; install the platform print support |
| Cells show `#VALUE!` or errors | Check the expression in the entry line; errors are Python exceptions or function error values |
| Slow workbook | Reduce the grid shape (`Edit → Resize grid`), raise the cell timeout in Preferences |
| A file opens in safe mode | The file is not approved; `File → Approve file` after reviewing its macros |
| Missing menu translations | The string is not in `nxsheet/i18n.py` yet |
| AI model download fails | Check the network and free disk space; the app stays usable without the model |

## 15. Support

* Website: <https://nexuzy.in>
* Support: <support@nexuzy.in>
* Information: <info@nexuzy.in>
* Company: Nexuzy Lab
* License: MIT, see [LICENSE](../LICENSE)
