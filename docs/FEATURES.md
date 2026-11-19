# Nexuzy Sheet feature status

This page is the honest feature audit of Nexuzy Sheet **1.3.0**. Every row was
checked against the source code in this repository. Status meanings:

| Symbol | Meaning |
| --- | --- |
| ✅ | Implemented and reachable from the user interface |
| 🟡 | Partially implemented – works for the stated subset only |
| ❌ | Not implemented in this release |

Nexuzy Sheet is an MIT licensed desktop spreadsheet that runs Python in its
cells. It is **not** a full Excel replacement: collaborative cloud editing,
pivot tables, conditional formatting and a plugin marketplace are not part of
this release. Where a feature is missing, the row says so instead of promising
it.

## 1. Workbook and file management

| Feature | Status | Notes |
| --- | --- | --- |
| New workbook | ✅ | `File → New`, choose the grid shape |
| Multiple worksheets | 🟡 | Worksheets are called *tables* (`S[row, column, table]`), switched with the table tabs; up to 100 tables per workbook |
| Rename sheet | ❌ | Tables are numbered |
| Duplicate sheet | ❌ | Copy the cells into another table instead |
| Move/copy sheet between workbooks | ❌ | Cell ranges can be copied between windows |
| Delete sheet | ✅ | `Edit → Delete table`, table context menu |
| Hide/unhide sheet | ❌ | – |
| Workbook templates | ✅ | Invoice, Attendance Register, General Ledger, Payroll Sheet, Budget Planning (`nxsheet/templates.py`) |
| AutoSave | ✅ | `File → Auto save`; recovery copy every 120 s while there are unsaved changes (configurable in QSettings) |
| Version history | ✅ | `File → Version history…` lists recovery copies and up to 20 automatic backups per workbook |
| Import XLSX | ✅ | `openpyxl` based reader, formulas converted |
| Import XLS | ❌ | Legacy binary format is not read |
| Import CSV / TSV | ✅ | CSV import dialog with delimiter/encoding sniffing |
| Import ODS | ❌ | – |
| Export XLSX | ✅ | – |
| Export XLS | ✅ | Requires the optional `xlwt` package |
| Export CSV / TSV | ✅ | CSV export with configurable delimiter/encoding |
| Export PDF | ✅ | Qt print engine |
| Export ODS | ✅ | Requires the optional `odfpy` package |
| Print selected sheets/workbook | ✅ | Print area dialog, print preview, printing of the current table |
| Password protection | ❌ | Files can be *signed* (SHA based signature sidecar) but not encrypted |
| Recent files | ✅ | `File → Recent files` (5 entries) |

## 2. Spreadsheet editing

| Feature | Status | Notes |
| --- | --- | --- |
| Insert/delete/resize rows and columns | ✅ | Menu, toolbar and header context menus |
| Edit individual cells | ✅ | Entry line with undo stack |
| Cell selection | ✅ | Single, rectangular, row/column and selection mode |
| Multi-cell editing | ✅ | Typing/pasting applies to the whole selection |
| Copy & paste (content + formatting) | ✅ | Separate `Copy`/`Copy results` and copy/paste format actions |
| Cut & paste | ✅ | – |
| Drag & fill | 🟡 | Fill down / fill right for selections; no mouse fill handle |
| AutoFill sequences | ❌ | – |
| Flash Fill | ❌ | – |
| Undo & redo | ✅ | Qt undo stack for cell, format and structure changes |
| Find & replace | ✅ | Find dialog, find next, replace, replace all |
| Go to cell | ✅ | Row/column/table dialog |
| Merge cells | ✅ | Merge and unmerge via `Format → Merge cells` |
| Split text to columns | ❌ | – |
| Text wrapping | ✅ | Wrapped rendering inside cells |
| Freeze panes | ✅ | Frozen cells stay visible while scrolling |
| AutoFit columns and rows | ✅ | `Format → AutoFit columns / rows / selection` sizes cells to their content |
| Hide rows/columns | ❌ | – |
| Group rows/columns | ❌ | – |
| Cell comments | ❌ | – |
| Hyperlinks | ❌ | – |
| Data validation | ❌ | – |
| Named ranges | 🟡 | Python names/globals and macros, but no spreadsheet level named ranges |

## 3. Cell formatting and design

| Feature | Status | Notes |
| --- | --- | --- |
| Font family, size | ✅ | Format toolbar and `Format → Font…` |
| Bold, italic, underline | ✅ | Strikethrough too |
| Font colour, background colour | ✅ | Colour buttons |
| Cell borders, border styles | ✅ | Border menu with per-side and outline choices, eight widths |
| Horizontal and vertical alignment | ✅ | – |
| Number formatting | 🟡 | `TEXT`, `DOLLAR`, `FIXED`, `ROUND` functions; no cell-level number format dialog |
| Currency, percentage, date formats | 🟡 | Currency/date shortcodes in the Macro menu, `TEXT` patterns |
| Decimal precision | ✅ | `ROUND`, `ROUNDUP`, `ROUNDDOWN`, `TRUNC` |
| Custom number formats | 🟡 | Via `TEXT(value, format)` |
| Conditional formatting | ❌ | – |
| Gradient colour scales / data bars / icon sets | ❌ | – |
| Alternating row colours | ❌ | – |
| Cell styles | 🟡 | Copy/paste format and clone formatting work as a style brush |
| Table styles | ❌ | – |
| Format painter | ✅ | `Format → Copy format` / `Paste format`, `Clone formatting` |
| Clear formatting | ✅ | `Format → Default format` |
| Themes | 🟡 | Light and dark colour themes |
| Custom spreadsheet styles | ❌ | – |

## 4. Formula and calculation engine

The engine evaluates Python expressions in cells with an Excel compatible
function library (`nxsheet/lib/excel_functions.py`, 107 functions).

| Category | Available |
| --- | --- |
| Mathematical | `SUM`, `PRODUCT`, `ABS`, `ROUND`, `ROUNDUP`, `ROUNDDOWN`, `MOD`, `POWER`, `CEILING`, `FLOOR`, `MROUND`, `INT`, `TRUNC`, `SQRT`, `EXP`, `LN`, `LOG`, `LOG10`, `PI`, `RAND`, `RANDBETWEEN`, `GCD`, `LCM`, `SIGN`, `SUMSQ` |
| Statistical | `AVERAGE`, `AVERAGEIF`, `COUNT`, `COUNTA`, `COUNTBLANK`, `COUNTIF`, `MEDIAN`, `MAX`, `MIN`, `LARGE`, `SMALL`, `STDEV`, `STDEVP`, `VAR`, `VARP`, `RANK` |
| Logical | `IF`, `AND`, `OR`, `NOT`, `XOR`, `IFERROR`, `IFNA`, `TRUE`, `FALSE`, `NA` |
| Lookup | `VLOOKUP`, `HLOOKUP`, `INDEX`, `MATCH`, `CHOOSE` |
| Text | `LEFT`, `RIGHT`, `MID`, `LEN`, `TRIM`, `CONCAT`, `CONCATENATE`, `TEXTJOIN`, `SUBSTITUTE`, `REPLACE`, `FIND`, `SEARCH`, `EXACT`, `LOWER`, `UPPER`, `PROPER`, `REPT`, `VALUE`, `NUMBERVALUE`, `DOLLAR`, `FIXED`, `TEXT` |
| Date and time | `TODAY`, `NOW`, `DATE`, `TIME`, `DAY`, `MONTH`, `YEAR`, `HOUR`, `MINUTE`, `SECOND`, `WEEKDAY`, `DAYS`, `EDATE`, `EOMONTH`, `NETWORKDAYS` |
| Financial | `PMT`, `PV`, `FV`, `NPV`, `IRR`, `NPER`, `EFFECT` |
| Information | `ISBLANK`, `ISNUMBER`, `ISTEXT`, `ISERROR`, `ISNA` |

| Calculation feature | Status | Notes |
| --- | --- | --- |
| Formula bar | ✅ | Entry line dock with syntax highlighting |
| Formula autocomplete | ❌ | – |
| Function suggestions / insert function dialog | ✅ | `Insert function…` (`Shift+F3`) with search and signatures |
| Formula syntax validation | 🟡 | Python errors are reported per cell |
| Formula dependency tracking | ❌ | Dirty cells are recalculated, no dependency graph |
| Automatic recalculation | ✅ | On cell change |
| Manual calculation mode | ❌ | – |
| Relative / absolute / mixed references | ✅ | `S[row, column, table]` with selection-mode insertion of references |
| Cross-sheet formulas | ✅ | Third index selects the table |
| Named formulas | ❌ | Python globals in macros can act as shared names |
| Circular reference detection | 🟡 | Recursion is stopped by the calculation timeout, not reported as a cycle |
| Formula error messages | ✅ | Error text in the cell and in the status bar |
| Formula auditing | ❌ | – |
| Calculation chain | ❌ | – |
| Array formulas | 🟡 | Results can be numpy arrays and are rendered as arrays, but no `Ctrl+Shift+Enter` semantics |
| `IFS`, `SWITCH`, `XLOOKUP`, `DATEDIF`, `COUNTIFS`, `RATE`, `DSUM`, `DCOUNT`, `DAVERAGE`, `DMAX`, `DMIN` | ❌ | Not in 1.3.0 |
| Dynamic arrays (`FILTER`, `SORT`, `SORTBY`, `UNIQUE`, `SEQUENCE`) | ❌ | Not in 1.3.0 |

## 5. Data management

| Feature | Status |
| --- | --- |
| Sort ascending / descending | ✅ |
| Multi-column / advanced sorting | ❌ |
| Filter by value/text/date, custom filters, advanced filters | ❌ |
| Remove duplicates | ❌ |
| Data validation, dropdown lists | ❌ |
| Data cleaning, text to columns, normalisation | ❌ |
| Data grouping, subtotals, outlines | ❌ |
| Table creation, structured references | ❌ |
| Consolidation | ❌ |
| Import wizard | 🟡 CSV import dialog with type/digest selection |
| Export wizard | ✅ Export dialog with area and format selection |

## 6. Charts and visualisation

| Feature | Status | Notes |
| --- | --- | --- |
| Chart insertion | ✅ | `Macro → Insert chart…` creates matplotlib charts inside cells |
| Chart templates | ✅ | Chart template toolbar with matplotlib templates |
| Histogram, waterfall, funnel, radar, treemap, sunburst | 🟡 | Only chart types provided as matplotlib code templates; no dedicated one-click types |
| Combo charts | 🟡 | Possible through matplotlib code |
| Pivot charts | ❌ | – |
| Chart titles, axis formatting, data labels, legends, trendlines | 🟡 | Available through matplotlib code in the chart dialog |
| Dynamic charts | ✅ | Charts are Python code and follow cell data |
| Chart export as image | ✅ | SVG/PNG export of chart cells |
| Interactive charts | ❌ | – |

## 7. Pivot tables and advanced analysis

| Feature | Status |
| --- | --- |
| Pivot tables, drag-and-drop fields, grouping, aggregations, percentage calculations, pivot filters, slicers, timelines, pivot charts, refresh, drill-down | ❌ |
| What-if analysis, goal seek, scenario manager, data tables | ❌ |
| Solver integration | ❌ |
| Statistical/regression analysis, forecasting, descriptive statistics | 🟡 Through Python/numpy code in cells and macros |

## 8. Collaboration and sharing

All rows in this section are ❌ in 1.3.0: real-time multi-user editing,
presence, cell-level collaboration, comments/replies, @mentions, sharing
permissions, protected ranges, public/private links, activity history, change
tracking, conflict resolution and team workspaces.

Version restoration is covered locally by `File → Version history…`.

## 9. Automation and scripting

| Feature | Status | Notes |
| --- | --- | --- |
| Macro recording | ❌ | – |
| Macro execution and custom scripts | ✅ | Macro panel, Python code stored inside the workbook |
| JavaScript automation | ❌ | The automation language is Python |
| Python integration | ✅ | Cells and macros are Python |
| Scheduled tasks | ❌ | – |
| Automated calculations | ✅ | Recalculation on change |
| Automated reports / exports | 🟡 | Export actions can be scripted from macros |
| Conditional automation, event triggers | ❌ | – |
| Custom functions | ✅ | Define Python functions in the macro panel and use them in cells |
| Batch data processing | 🟡 Through macros |
| Automated import/export, workflow automation, script library, automation permissions | ❌ |
| Offline AI assistant | 🟡 | Qwen2.5-0.5B-Instruct GGUF (about 490 MB) is downloaded on the first start and runs locally; without the model or runtime the built-in action engine answers |

## 10. Security and permissions

| Feature | Status | Notes |
| --- | --- | --- |
| User authentication, 2FA, RBAC | ❌ | Desktop application without accounts |
| Workbook / sheet / cell permissions | 🟡 | Cells can be locked and files can be approved (safe mode) |
| Password-protected workbooks | ❌ | – |
| Encryption at rest | ❌ | Workbooks are compressed, not encrypted |
| Encryption in transit | ❌ | No network transfer |
| Secure sharing, session management, audit logs, login history, access revocation | ❌ | – |
| Backup and recovery | ✅ | Auto save recovery copies and automatic backups (1.3.0) |
| Data retention policies | ❌ | – |

## 11. Import and export compatibility

| Format | Import | Export | Note |
| --- | --- | --- | --- |
| XLSX | ✅ | ✅ | `openpyxl` |
| XLS | ❌ | ✅ | Export needs `xlwt` |
| CSV | ✅ | ✅ | – |
| TSV | ✅ | ✅ | Delimiter selectable |
| ODS | ❌ | ✅ | Export needs `odfpy` |
| PDF | ❌ | ✅ | – |
| HTML | ❌ | ✅ | – |
| JSON | ❌ | ✅ | – |
| XML | ❌ | ❌ | – |
| TXT | ❌ | ✅ | – |
| SVG | ❌ | ✅ | – |
| `.nix` | ✅ | ✅ | Native format |

## 12. User interface

| Feature | Status | Notes |
| --- | --- | --- |
| Professional ribbon interface | ❌ | Classic menu bar plus dockable toolbars |
| Home / Insert / Page Layout / Formulas / Data / Review / View / Developer toolbars | ❌ | Toolbars are Main, Format, Find and Macro |
| Formula input bar | ✅ | Entry line dock |
| Name box | ❌ | – |
| Worksheet tabs | ✅ | Table tabs below the grid |
| Status bar | ✅ | Sum, average, count, min, max, zoom, safe mode |
| Zoom controls | ✅ | 18 zoom levels |
| Context menus | ✅ | Grid, headers and table tabs |
| Keyboard shortcuts | ✅ | See the guide |
| Dark/light mode | ✅ | `View → Dark mode` |
| Full-screen mode | ✅ | `F11` |
| Customisable toolbar | ✅ | Show/hide actions per toolbar, icon size |
| Responsive layout | 🟡 | Dockable panes and splitter layout |
| Multi-window support | 🟡 | Four grid views of the same workbook, no multiple documents in one process |

## 13. Page layout and printing

| Feature | Status |
| --- | --- |
| Print area | ✅ |
| Print preview | ✅ |
| Page margins, orientation, paper size | 🟡 Through the native Qt print dialog |
| Page breaks | ❌ |
| Headers, footers, page numbering | ❌ |
| Repeat header rows | ❌ |
| Scaling | 🟡 Print zoom |
| PDF generation | ✅ |
| Print selected cells / entire table | ✅ |

## 14. Cloud and synchronisation

All cloud rows are ❌: cloud storage, automatic synchronisation, offline
editing with sync, multi-device access, cloud backups, shared folders,
organisation storage and storage quotas. Nexuzy Sheet is a local desktop
application; workbooks can live in any folder that a cloud client syncs.

## 15. Developer and extension system

| Feature | Status | Notes |
| --- | --- | --- |
| Custom formula development | ✅ | Python functions in the macro panel |
| Script editor | ✅ | Macro editor with syntax highlighting |
| Spreadsheet API | 🟡 | Python access to the grid model from macros |
| Formula / chart / import-export API | 🟡 | Reached through Python code, no formal API surface |
| Custom plugin system, extension marketplace | ❌ |
| Webhook integration, third-party integrations | ❌ |
| Custom toolbar extensions, developer console | ❌ |

## 16. Additional professional features

| Feature | Status |
| --- | --- |
| Financial / accounting / payroll / inventory / sales / HR / attendance / project templates | 🟡 Five templates ship: Invoice, Attendance Register, General Ledger, Payroll Sheet, Budget Planning |
| Invoice generator | ✅ Template with formula driven totals |
| Budget planner, expense tracker | 🟡 Budget Planning template; no expense tracker |
| Dashboards, business reports | ❌ |
| Data entry forms | ❌ |
| Barcode and QR code support | ❌ |
| Image insertion | ✅ |
| Shapes and diagrams | 🟡 Vector graphics (SVG) can be inserted and rendered in cells |
| Smart tables | ❌ |
| Cross-workbook references | ❌ |

## Android, iOS and web

Nexuzy Sheet is a desktop PyQt6 application for **Windows, macOS and Linux**.
There is no Android, iOS or browser build.
