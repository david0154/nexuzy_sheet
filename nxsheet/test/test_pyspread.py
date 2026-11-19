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
test_grid
=========

Unit tests for grid.py

"""

from contextlib import contextmanager
from os.path import abspath, dirname, join
import sys

import pytest

from PyQt6.QtWidgets import QApplication, QAbstractItemView


PYSPREADPATH = abspath(join(dirname(__file__) + "/.."))
LIBPATH = abspath(PYSPREADPATH + "/lib")


@contextmanager
def insert_path(path):
    sys.path.insert(0, path)
    yield
    sys.path.pop(0)


@contextmanager
def multi_selection_mode(grid):
    grid.clearSelection()
    old_selection_mode = grid.selectionMode()
    grid.setSelectionMode(QAbstractItemView.MultiSelection)
    yield
    grid.setSelectionMode(old_selection_mode)


with insert_path(PYSPREADPATH):
    from ..__init__ import APP_NAME, VERSION
    from ..main_window import MainWindow
    from ..commands import MakeButtonCell, RemoveButtonCell
    from ..lib.selection import Selection


app = QApplication.instance()
if app is None:
    app = QApplication([])
main_window = MainWindow()
zoom_levels = main_window.settings.zoom_levels


class TestMainWindow:
    """Unit tests for MainWindow in pyspread.py"""

    grid = main_window.grid
    cell_attributes = grid.model.code_array.cell_attributes

    def test_app_branding(self):
        """Unit test for app branding"""

        assert APP_NAME == "Nexuzy Sheet"
        assert VERSION == "1.0.0"
        assert main_window.windowTitle() == "Nexuzy Sheet"

    def test_default_theme_is_light(self):
        """The default app theme should match Excel-like light styling."""

        assert main_window.settings.theme_mode == "light"
        assert not main_window.main_window_actions.toggle_dark_mode.isChecked()

    def test_plain_text_input_is_displayed_as_text(self):
        """Bare text like 'name' should display as text instead of NameError."""

        assert main_window.grid.model.code_array._eval_cell((0, 0, 0), "name") == "name"

    def test_safe_mode(self):
        """Unit test for safe_mode"""

        main_window.safe_mode = True
        main_window.main_window_actions.approve.isEnabled()
        assert main_window.safe_mode

        main_window.safe_mode = False
        assert not main_window.main_window_actions.approve.isEnabled()
        assert not self.grid.model.code_array.result_cache
        assert not main_window.safe_mode

    def test_on_clear_globals(self):
        """Unit test for on_clear_globals"""

        self.grid.model.code_array.result_cache["test"] = "Testres"
        main_window.on_clear_globals()
        assert not self.grid.model.code_array.result_cache
