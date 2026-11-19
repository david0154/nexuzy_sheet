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

**Provides**

 * :class:`MacroPanel`

"""

import ast
from io import StringIO
from sys import exc_info
from traceback import print_exception

from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QDialogButtonBox, QSplitter
from PyQt6.QtWidgets import QTextEdit

try:
    from nxsheet.lib.spelltextedit import SpellTextEdit
    from nxsheet.lib.exception_handling import get_user_codeframe
except ImportError:
    from lib.spelltextedit import SpellTextEdit
    from lib.exception_handling import get_user_codeframe


class MacroPanel(QDialog):
    """The macro panel"""

    def __init__(self, parent, code_array):
        super().__init__()

        self.parent = parent
        self.code_array = code_array

        self._init_widgets()
        self._layout()

        self.update_()

        self.default_text_color = self.result_viewer.textColor()
        self.error_text_color = QColor("red")

        self.button_box.clicked.connect(self.on_apply)

    def _init_widgets(self):
        """Inititialize widgets"""

        font_family = self.parent.settings.macro_editor_font_family
        self.macro_editor = SpellTextEdit(self, font_family=font_family)

        self.result_viewer = QTextEdit(self)
        self.result_viewer.setReadOnly(True)

        self.splitter = QSplitter(Qt.Orientation.Vertical, self)

        self.splitter.addWidget(self.macro_editor)
        self.splitter.addWidget(self.result_viewer)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply)

    def _layout(self):
        """Layout dialog widgets"""

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def _is_invalid_code(self) -> str:
        """Preliminary code check

        Returns a string with the error message if code is not valid Python.
        If the code runs without errors, an empty string is returned.

        """

        try:
            ast.parse(self.code_array.macros)

        except Exception:
            # Grab the traceback and return it
            stringio = StringIO()
            excinfo = exc_info()
            # usr_tb will more than likely be none because ast throws
            # SytnaxErrors as occurring outside of the current execution frame
            usr_tb = get_user_codeframe(excinfo[2]) or None
            print_exception(excinfo[0], excinfo[1], usr_tb, None, stringio)
            return stringio.getvalue()
        else:
            return ''

    def on_apply(self):
        """Event handler for Apply button"""

        self.code_array.macros = self.macro_editor.toPlainText()

        err = self._is_invalid_code()
        if err:
            self.update_result_viewer(err=err)
        else:
            self.update_result_viewer(*self.code_array.execute_macros())
            self.parent.grid.model.safe_data_changed()

        self.parent.grid.gui_update()

    def update_(self):
        """Update macro content"""

        self.macro_editor.setPlainText(self.code_array.macros)
        self.on_apply()

    def update_result_viewer(self, result: str = "", err: str = ""):
        """Update event result following execution by main window

        :param result: Text to be shown in the result viewer in default color
        :param err: Text to be shown in the result viewer in error text color

        """

        self.result_viewer.clear()

        if result:
            self.result_viewer.append(result)
        if err:
            self.result_viewer.setTextColor(self.error_text_color)
            self.result_viewer.append(err)
            self.result_viewer.setTextColor(self.default_text_color)

