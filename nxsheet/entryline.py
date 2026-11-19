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

 * :class:`Entryline`

"""

from contextlib import contextmanager

from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QTextOption, QKeyEvent
from PyQt6.QtWidgets import QWidget, QMainWindow, QMessageBox

try:
    import nxsheet.commands as commands
    from nxsheet.lib.spelltextedit import SpellTextEdit, enchant
    from nxsheet.lib.string_helpers import quote
except ImportError:
    import commands
    from lib.spelltextedit import SpellTextEdit, enchant
    from lib.string_helpers import quote


class Entryline(SpellTextEdit):
    """The entry line for Nexuzy Sheet"""

    def __init__(self, main_window: QMainWindow):
        """

        :param main_window: Application main window

        """

        font_family = main_window.settings.entry_line_font_family
        super().__init__(line_numbers=False, font_family=font_family)

        self.main_window = main_window

        min_height = self.cursorRect().y() + self.cursorRect().height() + 20
        self.setMinimumHeight(min_height)

        self.setWordWrapMode(QTextOption.WrapMode.WrapAnywhere)

        self.installEventFilter(self)

        self.last_key = None

        # self.highlighter.setDocument(self.document())

    # Overrides

    def eventFilter(self, source: QWidget, event: QEvent):
        """Quotes editor content for <Ctrl>+<Enter> and <Ctrl>+<Return>

        Overrides SpellTextEdit default shortcut. Counts as undoable action.

        :param source: Source widget of event
        :param event: Event to be filtered

        """

        if event.type() == QEvent.Type.ShortcutOverride \
           and event.modifiers() == Qt.KeyboardModifier.ControlModifier \
           and source == self \
           and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):

            focused_grid = self.main_window.focused_grid
            code = quote(source.toPlainText())

            index = focused_grid.currentIndex()
            description = f"Quote code for cell {index}"
            cmd = commands.SetCellCode(code, focused_grid.model, index,
                                       description)
            self.main_window.undo_stack.push(cmd)
            focused_grid.setFocus()
            focused_grid.selectionModel().clearSelection()
            focused_grid.current = (focused_grid.row + 1, focused_grid.column,
                                    focused_grid.table)
            return False

        return QWidget.eventFilter(self, source, event)

    @contextmanager
    def disable_updates(self):
        """Disables updates and highlighter"""

        doc = self.highlighter.document()
        self.highlighter.setDocument(None)
        self.main_window.entry_line.setUpdatesEnabled(False)
        yield
        self.main_window.entry_line.setUpdatesEnabled(True)
        self.highlighter.setDocument(doc)

    def keyPressEvent(self, event: QKeyEvent):
        """Key press event filter

        :param event: Key event

        """

        grid = self.main_window.focused_grid

        self.last_key = event.key()

        if self.last_key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                self.insertPlainText('\n')
            else:
                if grid.selection_mode:
                    grid.set_selection_mode(False)
                else:
                    self.store_data()
                    grid.row += 1
            return
        elif self.last_key == Qt.Key.Key_Tab:
            self.store_data()
            grid.column += 1
            return
        elif self.last_key == Qt.Key.Key_Escape:
            grid.on_current_changed()
            grid.setFocus()
            return
        elif self.last_key == Qt.Key.Key_Insert:
            grid.set_selection_mode(not grid.selection_mode)
            return

        return super().keyPressEvent(event)

    def store_data(self):
        """Stores current entry line data in grid model"""

        grid = self.main_window.focused_grid

        index = grid.currentIndex()
        model = grid.model

        description = f"Set code for cell {index}"
        command = commands.SetCellCode(self.toPlainText(), model, index,
                                       description)
        self.main_window.undo_stack.push(command)

    def on_toggle_spell_check(self, signal: bool):
        """Spell check toggle event handler

        :param signal: Spell check is enabled if True

        """

        if signal and enchant is None:
            QMessageBox.information(
                self, "Spell checker unavailable",
                "Spell checking requires the optional PyEnchant package and "
                "an installed Enchant dictionary. Install pyenchant and a "
                "dictionary, then restart Nexuzy Sheet.")
            self.actions.toggle_spell_checker.setChecked(False)
            return

        self.highlighter.enable_enchant = bool(signal)
        self.highlighter.rehighlight()

    def setPlainText(self, text: str):
        """Overides setPlainText

        Additionally shows busy cursor and disables highlighter on long texts,
        and omits identical replace.

        :param text: Text to be set

        """

        is_long = (text is not None
                   and len(text) > self.main_window.settings.highlighter_limit)

        if text == self.toPlainText():
            return

        if is_long:
            with self.main_window.workflows.busy_cursor():
                self.highlighter.setDocument(None)
                super().setPlainText(text)
        else:
            super().setPlainText(text)

