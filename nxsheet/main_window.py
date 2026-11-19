#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Developed by Nexuzy Lab
#
# Nexuzy Sheet is released under the MIT License.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# License: MIT License
# https://opensource.org/licenses/MIT
#
# Project: Nexuzy Sheet
# Developer: Nexuzy Lab
# Copyright: © 2026 Nexuzy Lab
# --------------------------------------------------------------------

"""

Nexuzy Sheet
============

- Excel-like Python spreadsheet application
- Run this script to start the application.

**Provides**

* MainApplication: Initial command line operations and application launch
* :class:`MainWindow`: Main windows class

"""

from collections.abc import Iterable
import os
import threading
from pathlib import Path
import sys

from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QTimer, QRectF, QSize
from PyQt6.QtGui import QColor, QFont, QPainter, QUndoStack, QPalette
from PyQt6.QtWidgets import (QWidget, QMainWindow, QApplication,
                             QMessageBox, QDockWidget, QVBoxLayout,
                             QStyleOptionViewItem, QSplitter, QProgressDialog)
try:
    from PyQt6.QtSvgWidgets import QSvgWidget
except ImportError:
    QSvgWidget = None
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

try:
    from nxsheet.__init__ import AI_NAME, VERSION, APP_NAME
    from nxsheet.settings import Settings, WEB_URL, AUTHORS
    from nxsheet.icons import Icon, IconPath
    from nxsheet.grid import Grid, TableChoice
    from nxsheet.grid_renderer import painter_save
    from nxsheet.entryline import Entryline
    from nxsheet.menus import MenuBar
    from nxsheet.themes import ColorRole
    from nxsheet.toolbar import (MainToolBar, FindToolbar, FormatToolbar,
                                  MacroToolbar)
    from nxsheet.actions import MainWindowActions
    from nxsheet.workflows import Workflows
    from nxsheet.widgets import Widgets
    from nxsheet.dialogs import (ApproveWarningDialog, PreferencesDialog,
                                  ManualDialog, TutorialDialog,
                                  PrintAreaDialog, PrintPreviewDialog,
                                  AboutDialog)
    from nxsheet.installer import DependenciesDialog
    from nxsheet.interfaces.pys import qt62qt5_fontweights
    from nxsheet.autosave import AutoSaveManager, VersionHistoryDialog
    from nxsheet import i18n
    from nxsheet.panels import MacroPanel
    from nxsheet.ai.engine import (NexuzyAIController, QWEN_MODEL_URL,
                                    QWEN_FILENAME)
    from nxsheet.lib.hashing import genkey
    from nxsheet.model.model import CellAttributes
except ImportError:
    from __init__ import AI_NAME, VERSION, APP_NAME
    from settings import Settings, WEB_URL, AUTHORS
    from icons import Icon, IconPath
    from grid import Grid, TableChoice
    from grid_renderer import painter_save
    from entryline import Entryline
    from menus import MenuBar
    from themes import ColorRole
    from toolbar import MainToolBar, FindToolbar, FormatToolbar, MacroToolbar
    from actions import MainWindowActions
    from workflows import Workflows
    from widgets import Widgets
    from dialogs import (ApproveWarningDialog, PreferencesDialog, ManualDialog,
                         TutorialDialog, PrintAreaDialog, PrintPreviewDialog,
                         AboutDialog)
    from installer import DependenciesDialog
    from interfaces.pys import qt62qt5_fontweights
    from autosave import AutoSaveManager, VersionHistoryDialog
    import i18n
    from panels import MacroPanel
    from ai.engine import NexuzyAIController, QWEN_MODEL_URL, QWEN_FILENAME
    from lib.hashing import genkey
    from model.model import CellAttributes


LICENSE = "MIT License"

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


class MainWindow(QMainWindow):
    """Nexuzy Sheet main window"""

    gui_update = pyqtSignal(dict)

    #: Emitted with the AI setup result of the background model download
    ai_stack_ready = pyqtSignal(dict)
    #: Queued automatically when emitted from the AI setup worker thread.
    ai_download_progress = pyqtSignal(str)
    ai_action_ready = pyqtSignal(object)

    def __init__(self, filepath: Path = Path(),
                 default_settings: bool = False):
        """
        :param filepath: File path for inital file to be opened
        :param default_settings: Ignore stored `QSettings` and use defaults

        """

        super().__init__()

        self.grid_header_spreadsheet_format = False

        self._loading = True  # For initial loading of Nexuzy Sheet
        self.prevent_updates = False  # Prevents setData updates in grid

        self.settings = Settings(self, reset_settings=default_settings)
        self.workflows = Workflows(self)
        self.undo_stack = QUndoStack(self)
        self.refresh_timer = QTimer()

        self._init_widgets()

        self.main_window_actions = MainWindowActions(self)
        self.main_window_toolbar_actions = MainWindowActions(self,
                                                             shortcuts=False)

        self._init_window()
        self._init_toolbars()

        self.settings.restore()
        if self.settings.signature_key is None:
            self.settings.signature_key = genkey()
        if self.settings.theme_mode not in {"light", "dark"}:
            self.settings.theme_mode = "light"

        self.apply_theme(self.settings.theme_mode)
        self.set_toolbar_icon_size(self.settings.toolbar_icon_size)

        # User interface language
        i18n.set_language(self.settings.language)
        i18n.apply_to(self)
        self.menuBar().update_language_menu()

        # Auto save, automatic backups and version history
        self.autosave = AutoSaveManager(self)
        self.autosave.start()
        self.main_window_actions.autosave_toggle.setChecked(
            self.settings.autosave_enabled)

        # Print area for print requests
        self.print_area = None

        # Update recent files in the file menu
        self.menuBar().file_menu.history_submenu.update_()

        # Update toolbar toggle checkboxes
        self.update_action_toggles()

        # Update the GUI so that everything matches the model
        cell_attributes = self.grid.model.code_array.cell_attributes
        attributes = cell_attributes[self.grid.current]
        self.on_gui_update(attributes)

        self._last_focused_grid = self.grid

        self._loading = False
        self._previous_window_state = self.windowState()

        # Open initial file if provided by the command line
        if filepath is not None:
            if self.workflows.filepath_open(filepath):
                self.workflows.update_main_window_title()
            else:
                msg = f"File '{filepath}' could not be opened."
                self.statusBar().showMessage(msg)

        if not self.isVisible():
            self.show()

        self.settings.changed_since_save = False

    def _init_window(self):
        """Initialize main window components"""

        self.setWindowTitle(APP_NAME)
        window_icon = (Icon.app_ico if sys.platform.startswith("win")
                       else Icon.app)
        self.setWindowIcon(window_icon)

        # Safe mode widget
        self.safe_mode_widget = QSvgWidget(str(IconPath.safe_mode),
                                           self.statusBar())
        msg = f"{APP_NAME} is in safe mode.\nExpressions are not evaluated."
        self.safe_mode_widget.setToolTip(msg)
        self.statusBar().addPermanentWidget(self.safe_mode_widget)
        self.safe_mode_widget.hide()

        # Selection mode widget
        self.selection_mode_widget = QSvgWidget(str(IconPath.selection_mode),
                                                self.statusBar())
        msg = "Selection mode active. Cells cannot be edited.\n" + \
              "Selecting cells adds relative references into the entry " + \
              "line. Additionally pressing `Meta` switches to absolute " + \
              "references.\nEnd selection mode by clicking into the entry " + \
              "line or with `Esc` when focusing the grid."
        self.selection_mode_widget.setToolTip(msg)
        self.statusBar().addPermanentWidget(self.selection_mode_widget)
        self.selection_mode_widget.hide()

        # Disable the approve fiel menu button
        self.main_window_actions.approve.setEnabled(False)

        self.setMenuBar(MenuBar(self))

        # F11 should work even of the menubar is hidden
        self.addAction(self.main_window_actions.fullscreen)
        self.addAction(self.main_window_actions.toggle_macro_dock)

    def resizeEvent(self, event: QEvent):
        """Overloaded, aborts on self._loading

        :param event: Resize event

        """

        if self._loading:
            return

        super().resizeEvent(event)

    def closeEvent(self, event: QEvent = None):
        """Overloaded, allows saving changes or canceling close

        :param event: Any QEvent

        """

        if event:
            event.ignore()

        # Keep a recovery copy of unsaved changes before closing
        autosave = getattr(self, "autosave", None)
        if autosave is not None:
            autosave.backup_on_close()

        self.workflows.file_quit()  # has @handle_changed_since_save decorator

    def dragEnterEvent(self, event: QEvent = None):
        """Overloaded, accept the dragging of files into Nexuzy Sheet

        :param event: Any QEvent

        """

        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QEvent = None):
        """Overloaded, accept the moving of files over Nexuzy Sheet

        :param event: Any QEvent

        """

        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QEvent = None):
        """Overloaded, catch the dropping of files into Nexuzy Sheet

        :param event: Any QEvent

        """

        for url in event.mimeData().urls():
            if url.isLocalFile():
                filepath = Path(url.toLocalFile())
                self.workflows.file_open_recent(filepath)
                break

    def _init_widgets(self):
        """Initialize widgets"""

        self.widgets = Widgets(self)

        self.entry_line = Entryline(self)

        self.vsplitter = QSplitter(Qt.Orientation.Vertical, self)
        self.hsplitter_1 = QSplitter(Qt.Orientation.Horizontal, self)
        self.hsplitter_2 = QSplitter(Qt.Orientation.Horizontal, self)

        # Set up the table choice first
        _no_tables = self.settings.shape[2]
        self.table_choice = TableChoice(self, _no_tables)

        # We have one main view that is used as default view
        self.grid = Grid(self)
        # Further views of the grid
        self.grid_2 = Grid(self, self.grid.model)
        self.grid_3 = Grid(self, self.grid.model)
        self.grid_4 = Grid(self, self.grid.model)

        self.grids = [self.grid, self.grid_2, self.grid_3, self.grid_4]

        self.macro_panel = MacroPanel(self, self.grid.model.code_array)

        self.main_panel = QWidget(self)

        self.ai_controller = NexuzyAIController(
            base_dir=str(Path.home() / ".nexuzy_sheet"))
        self.ai_stack_ready.connect(self.on_ai_stack_ready)
        self.ai_download_progress.connect(self.on_ai_download_progress)
        self.ai_action_ready.connect(self.on_ai_action_ready)

        self.entry_line_dock = QDockWidget("Entry Line", self)
        self.entry_line_dock.setObjectName("Entry Line Panel")
        self.entry_line_dock.setWidget(self.entry_line)
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea,
                           self.entry_line_dock)
        self.resizeDocks([self.entry_line_dock], [10],
                         Qt.Orientation.Horizontal)

        self.ai_dock = QDockWidget("Ask Nexuzy AI", self)
        self.ai_dock.setObjectName("AI Panel")
        self.ai_dock.setWidget(self._create_ai_panel())
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,
                           self.ai_dock)
        self.ai_dock.setVisible(True)
        self.ai_dock.raise_()

        self.macro_dock = QDockWidget("Macros", self)
        self.macro_dock.setObjectName("Macro Panel")
        self.macro_dock.setWidget(self.macro_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea,
                           self.macro_dock)

        self.central_layout = QVBoxLayout(self.main_panel)
        self._layout()

        self.entry_line_dock.installEventFilter(self)
        self.macro_dock.installEventFilter(self)

        QApplication.instance().focusChanged.connect(self.on_focus_changed)
        self.gui_update.connect(self.on_gui_update)
        self.refresh_timer.timeout.connect(self.on_refresh_timer)

        self.ai_dock.raise_()

        # Connect widgets only to first grid
        self.widgets.text_color_button.colorChanged.connect(
            self.grid.on_text_color)
        self.widgets.background_color_button.colorChanged.connect(
            self.grid.on_background_color)
        self.widgets.line_color_button.colorChanged.connect(
            self.grid.on_line_color)
        self.widgets.font_combo.fontChanged.connect(self.grid.on_font)
        self.widgets.font_size_combo.fontSizeChanged.connect(
            self.grid.on_font_size)

        # Clear globals to make pycel work
        self.on_clear_globals()

    def _create_ai_panel(self):
        """Create a compact local AI panel for user commands and template selection."""

        from PyQt6.QtWidgets import (QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QHBoxLayout,
                                      QComboBox, QLabel, QGroupBox)

        panel = QWidget(self)
        layout = QVBoxLayout(panel)

        # Template selection section
        template_group = QGroupBox("Templates", panel)
        template_layout = QHBoxLayout(template_group)

        self.template_combo = QComboBox(panel)
        self._populate_template_combo()

        self.template_load_btn = QPushButton("Load Template", panel)
        self.template_load_btn.setToolTip("Load selected template with sample data")
        self.template_load_btn.clicked.connect(self.on_load_template)

        template_layout.addWidget(QLabel("Choose:", panel))
        template_layout.addWidget(self.template_combo)
        template_layout.addWidget(self.template_load_btn)
        template_group.setMaximumHeight(60)
        layout.addWidget(template_group)

        # AI text input section
        self.ai_input = QLineEdit(panel)
        self.ai_input.setPlaceholderText("Ask anything about this spreadsheet...")
        self.ai_input.returnPressed.connect(self.on_ai_submit)

        self.ai_submit = QPushButton("Ask AI", panel)
        self.ai_submit.clicked.connect(self.on_ai_submit)

        # Upload buttons row
        buttons_layout = QHBoxLayout()
        
        self.ai_invoice_btn = QPushButton("📄 Invoice", panel)
        self.ai_invoice_btn.setToolTip("Upload invoice/bill PDF to auto-fill invoice template")
        self.ai_invoice_btn.clicked.connect(self.on_ai_import_invoice)
        
        self.ai_image_btn = QPushButton("🖼️ Image", panel)
        self.ai_image_btn.setToolTip("Extract table from image")
        self.ai_image_btn.clicked.connect(self.on_ai_import_image)
        
        self.ai_pdf_btn = QPushButton("📕 PDF", panel)
        self.ai_pdf_btn.setToolTip("Extract content from PDF and apply to template")
        self.ai_pdf_btn.clicked.connect(self.on_ai_import_pdf)
        
        buttons_layout.addWidget(self.ai_invoice_btn)
        buttons_layout.addWidget(self.ai_image_btn)
        buttons_layout.addWidget(self.ai_pdf_btn)

        self.ai_output = QTextEdit(panel)
        self.ai_output.setReadOnly(True)
        self.ai_output.setPlaceholderText("AI suggestions and template info appear here...")
        self.ai_output.setMaximumHeight(120)

        layout.addWidget(self.ai_input)
        layout.addWidget(self.ai_submit)
        layout.addLayout(buttons_layout)
        layout.addWidget(self.ai_output)
        panel.setLayout(layout)
        return panel

    def _populate_template_combo(self):
        """Populate template list with a safe fallback if the AI controller is unavailable."""
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItem("-- Select Template --", None)

        try:
            templates = self.ai_controller.get_available_templates()
            if templates:
                for template_id, template_name in templates.items():
                    self.template_combo.addItem(template_name, template_id)
            else:
                for template_id, template_name in {
                    "invoice": "Invoice",
                    "attendance": "Attendance Register",
                    "ledger": "General Ledger",
                    "payroll": "Payroll Sheet",
                    "budget": "Budget Planning",
                }.items():
                    self.template_combo.addItem(template_name, template_id)
        except Exception:
            for template_id, template_name in {
                "invoice": "Invoice",
                "attendance": "Attendance Register",
                "ledger": "General Ledger",
                "payroll": "Payroll Sheet",
                "budget": "Budget Planning",
            }.items():
                self.template_combo.addItem(template_name, template_id)
        finally:
            self.template_combo.blockSignals(False)

    def _cell_ref_to_index(self, cell_ref: str):
        """Convert A1-style references into row, column indices."""

        if not cell_ref:
            return self.grid.current[:2]

        match = __import__("re").match(r"^\s*([A-Za-z]+)([0-9]+)\s*$", str(cell_ref))
        if not match:
            return self.grid.current[:2]

        letters, row_number = match.groups()
        col = 0
        for char in letters.upper():
            col = col * 26 + (ord(char) - 64)
        row = int(row_number) - 1
        return row, col - 1

    def _insert_table(self, table, start_cell: str = None, merged_cells=None, styles=None):
        """Write a row/column table into the active grid from a start cell."""

        if not table:
            return

        start_row, start_col = self._cell_ref_to_index(start_cell or "A1") if start_cell else self.grid.current[:2]
        for row_idx, row in enumerate(table):
            for col_idx, value in enumerate(row):
                if value is None:
                    continue
                cell_index = self.grid.model.index(start_row + row_idx, start_col + col_idx)
                self.grid.model.setData(cell_index, value, Qt.ItemDataRole.EditRole, raw=True)

        if merged_cells:
            from nxsheet.model.model import CellAttribute
            from nxsheet.lib.attrdict import AttrDict
            from nxsheet.lib.selection import Selection

            for top, left, bottom, right in merged_cells:
                selection = Selection([], [], [], [], [(start_row + top, start_col + left)])
                attr = CellAttribute(selection, self.grid.table, AttrDict([("merge_area", (start_row + top, start_col + left, start_row + bottom, start_col + right))]))
                self.grid.model.setData([self.grid.model.index(start_row + top, start_col + left)], attr, Qt.ItemDataRole.DecorationRole)

        if styles:
            from nxsheet.lib.attrdict import AttrDict
            from nxsheet.lib.selection import Selection
            from nxsheet.model.model import CellAttribute

            style_map = {
                "title_row": {"bgcolor": (31, 78, 121), "textcolor": (255, 255, 255), "fontweight": 75, "pointsize": 16},
                "header_row": {"bgcolor": (217, 225, 242), "fontweight": 75},
            }
            for style_key, row_styles in style_map.items():
                row_index = styles.get(style_key)
                if isinstance(row_index, int) and 0 <= row_index < len(table):
                    row_width = len(table[row_index])
                    if row_width:
                        selection = Selection(
                            [(start_row + row_index, start_col)],
                            [(start_row + row_index, start_col + row_width - 1)],
                            [], [], [],
                        )
                        attr = CellAttribute(
                            selection, self.grid.table, AttrDict(row_styles))
                        self.grid.model.setData(
                            [], attr, Qt.ItemDataRole.DecorationRole)
            self.grid.model.safe_data_changed()

    def on_ai_submit(self):
        """Submit a user command and apply the returned action to the spreadsheet."""

        question = self.ai_input.text().strip()
        if not question:
            return

        # Product and formula questions are answered exactly, without the model.
        direct = self.ai_controller.direct_answer(question)
        if direct is not None:
            self.ai_output.setPlainText(direct)
            return

        manager = self.ai_controller.model_manager
        if not manager.model_ready() or not manager.llama_runtime_ready:
            self.ai_output.setPlainText(
                "The offline AI model is being prepared; this happens only "
                "once. Submit the request again when the download finishes.")
            self.start_ai_setup()
            return

        sheet_data = []
        code_array = self.grid.model.code_array
        current_row, current_col, current_table = self.grid.current
        active_cell = self.grid.current
        active_table = self.grid.table
        for row in range(max(0, current_row - 10), min(code_array.shape[0], current_row + 11)):
            values = []
            for col in range(max(0, current_col - 5), min(code_array.shape[1], current_col + 6)):
                value = code_array[row, col, current_table]
                values.append(value if isinstance(value, (str, int, float, bool)) or value is None else str(value)[:200])
            sheet_data.append(values)

        self.ai_submit.setEnabled(False)
        self.ai_output.setPlainText("Loading offline Qwen and generating a spreadsheet action...")

        def worker():
            try:
                action = self.ai_controller.handle_text_request(question, {
                    "sheet": {
                        "current_cell": active_cell,
                        "table": active_table,
                        "data": sheet_data,
                    }
                })
            except Exception as exc:
                from nxsheet.ai.engine import AIAction
                action = AIAction(action="error",
                              explanation=f"{AI_NAME} failed: {exc}")
            self.ai_action_ready.emit(action)

        threading.Thread(target=worker, daemon=True, name="nexuzy-ai-request").start()

    def on_ai_action_ready(self, action):
        self.ai_submit.setEnabled(True)

        if action.action == "formula" and action.formula and action.cell:
            row, col = self._cell_ref_to_index(action.cell)
            index = self.grid.model.index(row, col)
            self.grid.model.setData(index, action.formula, Qt.ItemDataRole.EditRole, raw=True)
            self.ai_output.setPlainText(
                f"Formula written to {action.cell}: {action.formula}. "
                f"Generated with {AI_NAME}."
            )
        elif action.action == "import_table" and action.data:
            self._insert_table(action.data, action.cell or "A1", merged_cells=getattr(action, "merged_cells", None), styles=getattr(action, "styles", None))
            self.ai_output.setPlainText(f"Imported {len(action.data)} rows from AI into the sheet.")
        elif action.action == "explain_formula":
            self.ai_output.setPlainText(action.explanation or "No explanation available.")
        else:
            message = action.explanation or f"AI action: {action.action}"
            if action.action in {"find", "error"}:
                message = action.explanation or f"Qwen action: {action.action}"
            self.ai_output.setPlainText(message)

        self.ai_input.clear()

    def on_load_template(self):
        """Load selected template into the spreadsheet."""
        
        template_id = self.template_combo.currentData()
        if not template_id:
            self.ai_output.setPlainText("Please select a template first.")
            return
        
        try:
            action = self.ai_controller.load_template(template_id)
            
            if action.action == "import_table" and action.data:
                self._insert_table(action.data, action.cell or "A1", merged_cells=getattr(action, "merged_cells", None), styles=getattr(action, "styles", None))
                self.ai_output.setPlainText(
                    action.explanation or f"Loaded template with {len(action.data)} rows."
                )
            else:
                self.ai_output.setPlainText("Could not load template.")
        except Exception as exc:
            self.ai_output.setPlainText(f"Error loading template: {str(exc)}")

    def on_ai_import_image(self):
        """Open an image and write recognized table rows into the current cell selection."""

        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(self, "Select image", filter="Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)")
        if not file_path:
            return

        result = self.ai_controller.handle_image_request(file_path)
        if not result:
            self.ai_output.setPlainText("No table text was detected in the image.")
            return

        table = [[item.get("text") for item in result]]
        self._insert_table(table, "A1")
        self.ai_output.setPlainText(f"Imported {len(table)} row(s) from image into the active sheet.")

    def on_ai_import_pdf(self):
        """Open a PDF and import its extracted page data into the current cell selection."""

        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", filter="PDF (*.pdf)")
        if not file_path:
            return

        result = self.ai_controller.handle_pdf_request(file_path)
        if not result:
            self.ai_output.setPlainText("No PDF content was detected.")
            return

        self._insert_table([[entry.get("page", str(i + 1))] for i, entry in enumerate(result)], "A1")
        self.ai_output.setPlainText(f"Imported PDF page metadata for {len(result)} page(s).")

    def on_ai_import_invoice(self):
        """Open an invoice/bill document and convert it to spreadsheet format with template styling."""

        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select invoice or bill",
            filter="Documents (*.pdf *.jpg *.jpeg *.png *.bmp);;PDF (*.pdf);;Images (*.jpg *.jpeg *.png *.bmp)"
        )
        if not file_path:
            return

        try:
            # Extract invoice data and populate into invoice template
            action = self.ai_controller.handle_pdf_with_template(file_path, template_name="invoice")
            
            if action.action == "import_table" and action.data:
                self._insert_table(action.data, action.cell or "A1", merged_cells=getattr(action, "merged_cells", None), styles=getattr(action, "styles", None))
                self.ai_output.setPlainText(
                    action.explanation or f"Imported invoice with {len(action.data)} rows."
                )
            else:
                self.ai_output.setPlainText("Could not extract invoice data.")
        except Exception as exc:
            self.ai_output.setPlainText(f"Error processing invoice: {str(exc)}")

    def _layout(self):
        """Layouts for main window"""

        self.central_layout.addWidget(self.vsplitter)
        self.central_layout.addWidget(self.grid.table_choice)

        self.vsplitter.addWidget(self.hsplitter_1)
        self.vsplitter.addWidget(self.hsplitter_2)

        self.hsplitter_1.addWidget(self.grid)
        self.hsplitter_1.addWidget(self.grid_2)
        self.hsplitter_2.addWidget(self.grid_3)
        self.hsplitter_2.addWidget(self.grid_4)

        self.vsplitter.setSizes([1, 0])
        self.hsplitter_1.setSizes([1, 0])
        self.hsplitter_2.setSizes([1, 0])

        self.main_panel.setLayout(self.central_layout)
        self.setCentralWidget(self.main_panel)

    def eventFilter(self, source: QWidget, event: QEvent) -> bool:
        """Overloaded event filter for handling QDockWidget close events

        Updates the menu if the macro panel is closed.

        :param source: Source widget of event
        :param event: Any QEvent

        """

        if event.type() == QEvent.Type.Close and isinstance(source,
                                                            QDockWidget):
            if source.windowTitle() == "Macros":
                self.main_window_actions.toggle_macro_dock.setChecked(False)
            elif source.windowTitle() == "Entry Line":
                self.main_window_actions.toggle_entry_line_dock.setChecked(
                    False)
            elif source.windowTitle() == "Ask Nexuzy AI":
                self.main_window_actions.toggle_ai_dock.setChecked(False)

        return super().eventFilter(source, event)

    def _init_toolbars(self):
        """Initialize the main window toolbars"""

        self.main_toolbar = MainToolBar(self)
        self.macro_toolbar = MacroToolbar(self)
        self.find_toolbar = FindToolbar(self)
        self.format_toolbar = FormatToolbar(self)

        self.addToolBar(self.main_toolbar)
        self.addToolBar(self.macro_toolbar)
        self.addToolBar(self.find_toolbar)
        self.addToolBarBreak()
        self.addToolBar(self.format_toolbar)

    def set_toolbar_icon_size(self, size):
        """Sets the icon size for all toolbars"""

        toolbars = (self.main_toolbar, self.macro_toolbar, self.find_toolbar,
                    self.format_toolbar)

        for toolbar in toolbars:
            toolbar.setIconSize(QSize(size, size))

    def update_action_toggles(self):
        """Updates the toggle menu check states"""

        actions = self.main_window_actions

        maintoolbar_visible = self.main_toolbar.isVisibleTo(self)
        actions.toggle_main_toolbar.setChecked(maintoolbar_visible)

        macrotoolbar_visible = self.macro_toolbar.isVisibleTo(self)
        actions.toggle_macro_toolbar.setChecked(macrotoolbar_visible)

        formattoolbar_visible = self.format_toolbar.isVisibleTo(self)
        actions.toggle_format_toolbar.setChecked(formattoolbar_visible)

        findtoolbar_visible = self.find_toolbar.isVisibleTo(self)
        actions.toggle_find_toolbar.setChecked(findtoolbar_visible)

        entryline_visible = self.entry_line_dock.isVisibleTo(self)
        actions.toggle_entry_line_dock.setChecked(entryline_visible)

        macrodock_visible = self.macro_dock.isVisibleTo(self)
        actions.toggle_macro_dock.setChecked(macrodock_visible)

        ai_dock_visible = self.ai_dock.isVisibleTo(self)
        actions.toggle_ai_dock.setChecked(ai_dock_visible)

    @property
    def focused_grid(self):
        """Returns grid with focus or self if none has focus"""

        try:
            return self._last_focused_grid
        except AttributeError:
            return self.grid

    @property
    def safe_mode(self) -> bool:
        """Returns safe_mode state. In safe_mode cells are not evaluated."""

        return self.grid.model.code_array.safe_mode

    @safe_mode.setter
    def safe_mode(self, value: bool):
        """Sets safe mode.

        This triggers the safe_mode icon in the statusbar.

        If safe_mode changes from True to False then caches are cleared and
        macros are executed.

        :param value: Safe mode

        """

        if self.grid.model.code_array.safe_mode == bool(value):
            return

        self.grid.model.code_array.safe_mode = bool(value)

        if value:  # Safe mode entered
            self.safe_mode_widget.show()
            # Enable approval menu entry
            self.main_window_actions.approve.setEnabled(True)
        else:  # Safe_mode disabled
            self.safe_mode_widget.hide()
            # Disable approval menu entry
            self.main_window_actions.approve.setEnabled(False)
            # Clear result cache
            self.grid.model.code_array.result_cache.clear()
            # Execute macros
            self.macro_panel.on_apply()

    def on_print(self):
        """Print event handler"""

        # Create printer
        printer = QPrinter(mode=QPrinter.PrinterMode.HighResolution)

        # Get print area
        self.print_area = PrintAreaDialog(self, self.grid,
                                          title="Print area").area
        if self.print_area is None:
            return

        # Create print dialog
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QPrintDialog.accepted:
            self.on_paint_request(printer)

        self.print_area = None

    def on_preview(self):
        """Print preview event handler"""

        # Create printer
        printer = QPrinter(mode=QPrinter.PrinterMode.HighResolution)

        # Get print area
        self.print_area = PrintAreaDialog(self, self.grid,
                                          title="Print area").area
        if self.print_area is None:
            return

        # Create print preview dialog
        dialog = PrintPreviewDialog(printer)

        dialog.paintRequested.connect(self.on_paint_request)
        dialog.exec()

        self.print_area = None

    def on_paint_request(self, printer: QPrinter):
        """Paints to printer

        :param printer: Target printer

        """

        painter = QPainter(printer)
        option = QStyleOptionViewItem()
        painter.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform)

        page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)

        rows = list(self.workflows.get_paint_rows(self.print_area.top,
                                                  self.print_area.bottom))
        columns = list(self.workflows.get_paint_columns(self.print_area.left,
                                                        self.print_area.right))

        if hasattr(self.print_area, "first") and hasattr(self.print_area, "last"):
            table_first, table_last = self.print_area.first, self.print_area.last
        else:
            table_first = table_last = self.grid.table

        tables = list(self.workflows.get_paint_tables(table_first, table_last))
        if not all((rows, columns, tables)):
            return

        old_table = self.grid.table

        for i, table in enumerate(tables):
            self.grid.table = table

            zeroidx = self.grid.model.index(0, 0)
            zeroidx_rect = self.grid.visualRect(zeroidx)

            minidx = self.grid.model.index(min(rows), min(columns))
            minidx_rect = self.grid.visualRect(minidx)

            maxidx = self.grid.model.index(max(rows), max(columns))
            maxidx_rect = self.grid.visualRect(maxidx)

            grid_width = maxidx_rect.x() + maxidx_rect.width() \
                - minidx_rect.x()
            grid_height = maxidx_rect.y() + maxidx_rect.height() \
                - minidx_rect.y()
            grid_rect = QRectF(minidx_rect.x() - zeroidx_rect.x(),
                               minidx_rect.y() - zeroidx_rect.y(),
                               grid_width, grid_height)

            self.settings.print_zoom = min(page_rect.width() / grid_width,
                                           page_rect.height() / grid_height)

            with painter_save(painter):
                painter.scale(self.settings.print_zoom,
                              self.settings.print_zoom)

                # Translate so that the grid starts at upper left paper edge
                painter.translate(zeroidx_rect.x() - minidx_rect.x(),
                                  zeroidx_rect.y() - minidx_rect.y())

                # Draw grid cells
                self.workflows.paint(painter, option, grid_rect, rows, columns)

            self.settings.print_zoom = None

            if i != len(tables) - 1:
                printer.newPage()

        self.grid.table = old_table

    def on_fullscreen(self):
        """Fullscreen toggle event handler"""

        if self.windowState() & Qt.WindowState.WindowFullScreen:
            previous_state = getattr(
                self, "_previous_window_state", Qt.WindowState.WindowNoState)
            if previous_state & Qt.WindowState.WindowMaximized:
                self.showMaximized()
            elif previous_state & Qt.WindowState.WindowMinimized:
                self.showMinimized()
            else:
                self.showNormal()
            for widget_name in self.settings.widget_names[1:]:
                widget = getattr(self, widget_name)
                widget.setVisible(
                    getattr(self, "_previous_visibility", {}).get(
                        widget_name, True))
            visibility = getattr(self, "_previous_visibility", {})
            self.menuBar().setVisible(visibility.get("menu_bar", True))
            self.table_choice.setVisible(
                visibility.get("table_choice", True))
            self.statusBar().setVisible(
                visibility.get("status_bar", True))
        else:
            self._previous_window_state = self.windowState()
            self._previous_visibility = {
                "menu_bar": self.menuBar().isVisible(),
                "table_choice": self.table_choice.isVisible(),
                "status_bar": self.statusBar().isVisible(),
            }
            for widget_name in self.settings.widget_names[1:]:
                widget = getattr(self, widget_name)
                self._previous_visibility[widget_name] = widget.isVisible()
                widget.hide()
            self.menuBar().hide()
            self.table_choice.hide()
            self.statusBar().hide()

            self.setWindowState(Qt.WindowState.WindowFullScreen)

    def on_approve(self):
        """Approve the currently open workbook after explicit confirmation."""

        if not self.safe_mode:
            return

        if ApproveWarningDialog(self).choice:
            self.safe_mode = False
            self.grid.model.safe_data_changed()
            self.settings.changed_since_save = True
            self.statusBar().showMessage(
                "Workbook approved. Save it to trust it next time.")

    def on_clear_globals(self):
        """Clear globals event handler"""

        self.grid.model.code_array.result_cache.clear()

        # Clear globals
        self.grid.model.code_array.clear_globals()
        self.grid.model.code_array.reload_modules()

    def on_preferences(self):
        """Preferences event handler (:class:`dialogs.PreferencesDialog`) """

        data = PreferencesDialog(self).data

        if data is not None:
            max_file_history_changed = \
                self.settings.max_file_history != data['max_file_history']

            # Immediately adjust toolbar icon size
            if self.settings.toolbar_icon_size != data['toolbar_icon_size']:
                self.set_toolbar_icon_size(data['toolbar_icon_size'])

            # Dialog has been approved --> Store data to settings
            for key in data:
                if key == "signature_key" and not data[key]:
                    data[key] = genkey()
                self.settings.__setattr__(key, data[key])

            # Immediately adjust file history in menu
            if max_file_history_changed:
                self.menuBar().file_menu.history_submenu.update_()

    def on_dependencies(self):
        """Dependancies installer (:class:`installer.InstallerDialog`) """

        dial = DependenciesDialog(self)
        dial.exec()

    def on_undo(self):
        """Undo event handler"""

        self.undo_stack.undo()

    def on_redo(self):
        """Undo event handler"""

        self.undo_stack.redo()

    def on_toggle_refresh_timer(self, toggled: bool):
        """Toggles periodic timer for frozen cells

        :param toggled: Toggle state

        """

        if toggled:
            self.grid.refresh_frozen_cells()
            self.refresh_timer.start(self.settings.refresh_timeout)
        else:
            self.refresh_timer.stop()

    def on_refresh_timer(self):
        """Event handler for self.refresh_timer.timeout

        Called for periodic updates of frozen cells.
        Does nothing if either the entry_line or a cell editor is active.

        """

        if not self.entry_line.hasFocus() \
           and self.grid.state() != self.grid.State.EditingState:
            self.grid.refresh_frozen_cells()

    def _toggle_widget(self, widget: QWidget, action_name: str, toggled: bool):
        """Toggles widget visibility and updates toggle actions

        :param widget: Widget to be toggled shown or hidden
        :param action_name: Name of action from Action class
        :param toggled: Toggle state

        """

        if toggled:
            widget.show()
        else:
            widget.hide()

        self.main_window_actions[action_name].setChecked(widget.isVisible())

    def apply_theme(self, theme_mode: str):
        """Applies a light or dark palette to the app."""

        theme_mode = (theme_mode or "light").lower()
        self.settings.theme_mode = theme_mode
        QApplication.instance().setStyle("Fusion")

        if theme_mode == "dark":
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor("#121212"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#F3F3F3"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#1E1E1E"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2A2A2A"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#1E1E1E"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#F3F3F3"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#F3F3F3"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#2A2A2A"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#F3F3F3"))
            palette.setColor(QPalette.ColorRole.BrightText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#5B9CFF"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Link, QColor("#7AB8FF"))
            palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#7AB8FF"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#A0A0A0"))
        else:
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor("#F5F6F7"))
            palette.setColor(QPalette.ColorRole.WindowText, QColor("#1F1F1F"))
            palette.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#F0F2F5"))
            palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#1F1F1F"))
            palette.setColor(QPalette.ColorRole.Text, QColor("#1F1F1F"))
            palette.setColor(QPalette.ColorRole.Button, QColor("#EEF1F4"))
            palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1F1F1F"))
            palette.setColor(QPalette.ColorRole.BrightText, QColor("#000000"))
            palette.setColor(QPalette.ColorRole.Highlight, QColor("#1A73E8"))
            palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
            palette.setColor(QPalette.ColorRole.Link, QColor("#0B57D0"))
            palette.setColor(QPalette.ColorRole.LinkVisited, QColor("#0B57D0"))
            palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#7A7A7A"))

        QApplication.instance().setPalette(palette)
        self.setPalette(palette)
        for grid in self.grids:
            grid.setPalette(palette)
        self.main_window_actions.toggle_dark_mode.setChecked(theme_mode == "dark")

    def on_toggle_dark_mode(self, toggled: bool):
        """Switch between light and dark mode."""

        self.apply_theme("dark" if toggled else "light")

    def on_toggle_gridheader_in_spreadsheet(self, toggled: bool):
        """Grid header format toggle event handler

        :param toggled: Toggle state
        """

        self.grid_header_spreadsheet_format = toggled
        self.grid.model.headerDataChanged.emit(
            Qt.Orientation.Vertical, 0, self.grid.model.shape[0])
        self.grid.model.headerDataChanged.emit(
            Qt.Orientation.Horizontal, 0, self.grid.model.shape[1])

    def on_toggle_main_toolbar(self, toggled: bool):
        """Main toolbar toggle event handler

        :param toggled: Toggle state

        """

        self._toggle_widget(self.main_toolbar, "toggle_main_toolbar", toggled)

    def on_toggle_macro_toolbar(self, toggled: bool):
        """Macro toolbar toggle event handler

        :param toggled: Toggle state

        """

        self._toggle_widget(self.macro_toolbar, "toggle_macro_toolbar",
                            toggled)

    def on_toggle_format_toolbar(self, toggled: bool):
        """Format toolbar toggle event handler

        :param toggled: Toggle state

        """

        self._toggle_widget(self.format_toolbar, "toggle_format_toolbar",
                            toggled)

    def on_toggle_find_toolbar(self, toggled: bool):
        """Find toolbar toggle event handler

        :param toggled: Toggle state

        """

        self._toggle_widget(self.find_toolbar, "toggle_find_toolbar", toggled)

    def on_toggle_entry_line_dock(self, toggled: bool):
        """Entryline toggle event handler

        :param toggled: Toggle state

        """

        self._toggle_widget(self.entry_line_dock, "toggle_entry_line_dock",
                            toggled)

    def on_toggle_macro_dock(self, toggled: bool):
        """Macro panel toggle event handler

        :param toggled: Toggle state

        """

        self._toggle_widget(self.macro_dock, "toggle_macro_dock", toggled)

    def on_toggle_ai_dock(self, toggled: bool):
        """AI dock toggle event handler

        :param toggled: Toggle state

        """

        self._toggle_widget(self.ai_dock, "toggle_ai_dock", toggled)

    def on_manual(self):
        """Show manual browser"""

        dialog = ManualDialog(self)
        dialog.show()

    def on_tutorial(self):
        """Show tutorial browser"""

        dialog = TutorialDialog(self)
        dialog.show()

    def gen_authors(self):
        """Generator of authors from the AUTHORS file"""

        for line in AUTHORS.split('\n'):
            yield line.strip()

    def on_about(self):
        """Show about dialog with company, website and MIT license"""

        dialog = AboutDialog(self)
        dialog.exec()

    def start_ai_setup(self):
        """Explicitly downloads or verifies the offline model in background."""

        if getattr(self, "_ai_setup_running", False):
            self.statusBar().showMessage("Offline AI model setup is already running.")
            return

        self._ai_setup_running = True
        self._ai_download_percent = 0
        self.statusBar().showMessage("Starting offline AI model setup...")
        self._ai_progress_dialog = QProgressDialog(
            "Connecting to Hugging Face and preparing the download...", "",
            0, 0, self)
        self._ai_progress_dialog.setWindowTitle("Downloading AI model")
        self._ai_progress_dialog.setCancelButton(None)
        self._ai_progress_dialog.setMinimumDuration(0)
        self._ai_progress_dialog.setWindowModality(
            Qt.WindowModality.WindowModal)
        self._ai_progress_dialog.show()

        def worker():
            """Downloads or verifies the local model"""

            try:
                def progress_callback(msg: str):
                    self.ai_download_progress.emit(msg)

                result = self.ai_controller.ensure_local_stack(
                    progress_callback=progress_callback
                )
            except Exception as error:  # Never break the UI on AI setup
                result = {"error": str(error)}
            self.ai_stack_ready.emit(result or {})

        try:
            thread = threading.Thread(target=worker, daemon=True,
                                      name="nexuzy-ai-setup")
            thread.start()
        except Exception as error:
            self._ai_setup_running = False
            self.statusBar().showMessage(
                f"Could not start offline AI setup: {error}", 30000)

    def on_ai_download_progress(self, message: str):
        """Update download status and progress on the GUI thread."""
        self.statusBar().showMessage(message)
        dialog = getattr(self, "_ai_progress_dialog", None)
        if dialog is None:
            return

        dialog.setLabelText(message)
        if message.startswith("Downloading") and message.rstrip().endswith("%"):
            try:
                percent = int(message.rsplit(":", 1)[1].strip().rstrip("%"))
            except ValueError:
                return
            if dialog.minimum() == dialog.maximum():
                dialog.setRange(0, 100)
            self._ai_download_percent = max(
                self._ai_download_percent, min(percent, 100))
            dialog.setValue(self._ai_download_percent)

    def on_ai_stack_ready(self, result: dict):
        """Shows the result of the offline AI model setup

        :param result: Result dictionary of the AI controller

        """

        self._ai_setup_running = False
        dialog = getattr(self, "_ai_progress_dialog", None)
        if dialog is not None:
            dialog.close()
            self._ai_progress_dialog = None
        model = (result or {}).get("model", {}) or {}
        status = model.get("status")
        runtime_download = (result or {}).get("runtime_download", {}) or {}
        if runtime_download.get("status") == "error":
            message = ("Offline AI runtime download failed: "
                       + str(runtime_download.get("error", "Unknown error")))
            self.statusBar().showMessage(message, 30000)
            QMessageBox.warning(self, "AI runtime download failed", message)
            return

        if status == "downloading":
            self.statusBar().showMessage("Starting offline AI model download...")
            return

        if status in ("ready", "downloaded"):
            message = ("Offline AI assistant ready: "
                       "Qwen2.5-0.5B-Instruct with llama.cpp")
            self.statusBar().showMessage(message, 20000)
        elif status == "error":
            message = "Offline AI model download failed: " + str(
                model.get("error", "Unknown download error"))
            self.statusBar().showMessage(message, 30000)
            QMessageBox.warning(self, "AI model download failed", message)
        elif status == "manual_required":
            self.statusBar().showMessage(
                "Offline AI model download did not start; retry from Help → "
                "Offline AI model.", 30000)
        elif (result or {}).get("error"):
            message = ("Offline AI assistant unavailable: "
                       f"{result['error']}")
            self.statusBar().showMessage(message, 30000)
            QMessageBox.warning(self, "AI model setup failed", message)
        else:
            message = ("Offline AI assistant runs without the local model; "
                       "spreadsheet actions still work.")
            self.statusBar().showMessage(message, 20000)

    def on_ai_model_info(self):
        """Shows the offline AI model source, path and download option"""

        manager = self.ai_controller.model_manager
        installed = ("installed" if manager.model_ready()
                     else "not downloaded yet")
        text = (
            f"{AI_NAME} - offline AI assistant\n\n"
            f"Product: {APP_NAME} {VERSION}\n"
            "Model: Qwen2.5-0.5B-Instruct (GGUF Q4_K_M)\n"
            "Known formulas: the complete built-in function library\n"
            "Size: about 491 MB\n"
            f"Source: {QWEN_MODEL_URL}\n"
            f"Local file: {manager.qwen_gguf}\n"
            f"File name: {QWEN_FILENAME}\n"
            f"Status: {installed}\n\n"
            "The model is downloaded only when you choose Download now and "
            "it is not already present. The llama.cpp inference runtime "
            "(about 25 MB) is installed alongside it. The model is loaded "
            "when you submit a prompt. "
            "Download requires an internet connection and about 500 MB of free space. "
            "No account or API key is required.")

        box = QMessageBox(self)
        box.setWindowTitle("Offline AI model")
        box.setText(text)
        download_button = box.addButton(
            "Download now", QMessageBox.ButtonRole.AcceptRole)
        box.addButton(QMessageBox.StandardButton.Close)
        box.exec()

        if box.clickedButton() is download_button:
            self.start_ai_setup()

    def on_toggle_autosave(self, checked: bool):
        """Enables or disables the automatic recovery copies

        :param checked: Check state of the Auto save action

        """

        self.settings.autosave_enabled = bool(checked)
        self.autosave.restart()
        state = "enabled" if checked else "disabled"
        self.statusBar().showMessage(f"Auto save {state}.")

    def on_version_history(self):
        """Shows the auto save recovery copies and automatic backups"""

        dialog = VersionHistoryDialog(self)
        dialog.exec()

    def set_language(self, code: str):
        """Switches the user interface language

        :param code: Language code such as ``"hi"`` or ``"ja"``

        """

        if code not in i18n.LANGUAGES:
            return

        self.settings.language = code
        i18n.set_language(code)
        i18n.apply_to(self)
        self.menuBar().update_language_menu()
        self.statusBar().showMessage(
            f"Language: {i18n.language_name(code)}")

    def on_focus_changed(self, old: QWidget, now: QWidget):
        """Handles grid clicks from entry line"""

        if old == self.grid and now == self.entry_line:
            self.grid.selection_mode = False

    def on_gui_update(self, attributes: CellAttributes):
        """GUI update that shall be called on each cell change

        :param attributes: Attributes of current cell

        """

        widgets = self.widgets
        menubar = self.menuBar()

        is_bold = attributes.fontweight is not None and \
            attributes.fontweight > qt62qt5_fontweights(QFont.Weight.Normal)
        self.main_window_actions.bold.setChecked(is_bold)
        self.main_window_toolbar_actions.bold.setChecked(is_bold)

        is_italic = attributes.fontstyle == QFont.Style.StyleItalic
        self.main_window_actions.italics.setChecked(is_italic)
        self.main_window_toolbar_actions.italics.setChecked(is_italic)

        self.main_window_actions.underline.setChecked(attributes.underline)
        self.main_window_toolbar_actions.underline.setChecked(
            attributes.underline)

        self.main_window_actions.strikethrough.setChecked(
            attributes.strikethrough)
        self.main_window_toolbar_actions.strikethrough.setChecked(
            attributes.strikethrough)

        renderer = attributes.renderer
        widgets.renderer_button.set_current_action(renderer)
        widgets.renderer_button.set_menu_checked(renderer)

        self.main_window_actions.freeze_cell.setChecked(attributes.frozen)
        self.main_window_toolbar_actions.freeze_cell.setChecked(
            attributes.frozen)

        self.main_window_actions.lock_cell.setChecked(attributes.locked)
        self.main_window_toolbar_actions.lock_cell.setChecked(
            attributes.locked)
        self.entry_line.setReadOnly(attributes.locked)

        self.main_window_actions.button_cell.setChecked(
            attributes.button_cell is not False)
        self.main_window_toolbar_actions.button_cell.setChecked(
            attributes.button_cell is not False)

        rotation = f"rotate_{int(attributes.angle)}"
        widgets.rotate_button.set_current_action(rotation)
        widgets.rotate_button.set_menu_checked(rotation)
        widgets.justify_button.set_current_action(attributes.justification)
        widgets.justify_button.set_menu_checked(attributes.justification)
        widgets.align_button.set_current_action(attributes.vertical_align)
        widgets.align_button.set_menu_checked(attributes.vertical_align)

        border_action = self.main_window_actions.border_group.checkedAction()
        if border_action is not None:
            icon = border_action.icon()
            menubar.format_menu.border_submenu.setIcon(icon)
            self.format_toolbar.border_menu_button.setIcon(icon)

        border_width_action = \
            self.main_window_actions.border_width_group.checkedAction()
        if border_width_action is not None:
            icon = border_width_action.icon()
            menubar.format_menu.line_width_submenu.setIcon(icon)
            self.format_toolbar.line_width_button.setIcon(icon)

        if attributes.textcolor is None:
            textcolor = self.grid.palette().color(ColorRole.text)
        else:
            textcolor = QColor(*attributes.textcolor)
        widgets.text_color_button.color = textcolor

        if attributes.bordercolor_bottom is None:
            linecolor = self.grid.palette().color(ColorRole.line)
        else:
            linecolor = QColor(*attributes.bordercolor_bottom)
        widgets.line_color_button.color = linecolor

        if attributes.bgcolor is None:
            bgcolor = self.grid.palette().color(ColorRole.bg)
        else:
            bgcolor = QColor(*attributes.bgcolor)
        widgets.background_color_button.color = bgcolor

        textfont = attributes.textfont
        if textfont is None:
            textfont = QFont().family()
        widgets.font_combo.font = textfont

        widgets.font_size_combo.size = attributes.pointsize

        self.main_window_actions.merge_cells.setChecked(
            attributes.merge_area is not None)
        self.main_window_toolbar_actions.merge_cells.setChecked(
            attributes.merge_area is not None)
        self.main_window_toolbar_actions.clone_formatting.setChecked(
            self.main_window_actions.clone_formatting.isChecked())


