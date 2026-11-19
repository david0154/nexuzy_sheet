# The `.nix` workbook format

Nexuzy Sheet 1.5.0 uses **`.nix`** as its native workbook extension. A `.nix`
file is a bzip2 compressed UTF-8 text workbook in the Nexuzy Sheet save format
version 2.0. It is the same format that earlier builds wrote with the `.nxs`
extension, so files can be exchanged between versions.

| Extension | Content | Notes |
| --- | --- | --- |
| `.nix` | bzip2 compressed workbook | **Default** for save and open |
| `.nxs` | bzip2 compressed workbook | Legacy alias, still read and written |
| `.nxl` | uncompressed workbook | Legacy uncompressed variant, still read |
| `.xlsx` | Office Open XML | Import only, needs `openpyxl` |
| `.csv`, `.tsv` | Delimited text | Import and export |

## Structure

Decompressed, a `.nix` file is a sequence of line oriented sections. Every
section starts with a bracketed header line, followed by tab separated values:

```text
[Nexuzy Sheet save file version]
2.0

[shape]
rows<TAB>columns<TAB>tables

[grid]
row<TAB>column<TAB>table<TAB>'cell code'

[attributes]
row<TAB>column<TAB>table<TAB>attribute dictionary

[row_heights]
row<TAB>table<TAB>height

[col_widths]
column<TAB>table<TAB>width

[macros]
python macro source
```

* **shape** stores the grid size. Cells outside the shape do not exist.
* **grid** stores the Python source of each non-empty cell. Results are
  computed when the file is opened.
* **attributes** stores formatting per cell: font, colours, borders, alignment,
  renderer, frozen/locked flags, merge area and rotation.
* **row_heights** / **col_widths** store custom dimensions.
* **macros** stores the workbook's Python macros, which are executed in the
  application namespace.

## Reading and writing without the GUI

```python
import bz2
from nxsheet.interfaces.pys import PysReader, PysWriter
from nxsheet.model.model import CodeArray
from nxsheet.settings import Settings

# Write
code_array = CodeArray((10, 5, 1), Settings(None))
code_array[0, 0, 0] = "SUM(S[1:9, 0, 0])"
with bz2.open("Report.nix", "wb") as outfile:
    for line in PysWriter(code_array):
        outfile.write(line.encode("utf-8"))

# Read
loaded = CodeArray((10, 5, 1), Settings(None))
with bz2.open("Report.nix", "rb") as infile:
    for _ in PysReader(infile, loaded):
        pass
print(loaded[0, 0, 0])
```

The auto save manager uses exactly this path
(`nxsheet.autosave.write_workbook`), which is why recovery copies are normal
workbooks that can be opened directly.

## File associations

The installers register `.nix` as a Nexuzy Sheet workbook:

* **Windows** – Inno Setup writes `HKA\Software\Classes\.nix` and the
  `NexuzySheet.Document` ProgID when the *associate* task is selected.
* **macOS** – `CFBundleDocumentTypes` lists `nix`, `nxl` and `nxs` in
  `Info.plist` and in the PyInstaller bundle.
* **Linux** – `nexuzy-sheet.desktop` and the shared MIME package
  `nexuzy-sheet-mime.xml` declare `application/x-nexuzy-sheet` for `*.nix`.

## Signatures and safe mode

A workbook can additionally have a `<name>.nix.sig` sidecar with a SHA-based
signature. The current file-open code performs its signature check for `.nix`
and `.nxs` paths; an invalid or missing signature places the workbook in safe
mode, where expressions are not evaluated. Signing is an integrity check, not
encryption: `.nix` files are not password protected.

## Auto save and backups

| Location | Content |
| --- | --- |
| `~/.nexuzy_sheet/autosave/<name>.autosave.nix` | Recovery copy of unsaved changes |
| `~/.nexuzy_sheet/backups/<name>/<name>-<timestamp>.nix` | Automatic backups, newest 20 kept |
