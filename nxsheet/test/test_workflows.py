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
test_workflows
==============

Unit tests for workflows.py

"""

from contextlib import contextmanager
from os.path import abspath, dirname, join
from pathlib import Path
import sys
from unittest.mock import PropertyMock, patch

import pytest

from PyQt6.QtCore import Qt, QItemSelection, QItemSelectionModel
from PyQt6.QtWidgets import QApplication

try:
    from nxsheet.dialogs import GridShapeDialog
except ImportError:
    from dialogs import GridShapeDialog


PYSPREADPATH = abspath(join(dirname(__file__) + "/.."))
LIBPATH = abspath(PYSPREADPATH + "/lib")


@contextmanager
def insert_path(path):
    sys.path.insert(0, path)
    yield
    sys.path.pop(0)


with insert_path(PYSPREADPATH):
    from ..main_window import MainWindow


app = QApplication.instance()
if app is None:
    app = QApplication([])
main_window = MainWindow()


class TestWorkflows:
    """Unit tests for Workflows in workflows.py"""

    workflows = main_window.workflows

    def test_busy_cursor(self):
        """Unit test for busy_cursor"""

        assert QApplication.overrideCursor() != Qt.CursorShape.WaitCursor

        with self.workflows.busy_cursor():
            assert QApplication.overrideCursor() == Qt.CursorShape.WaitCursor

        assert QApplication.overrideCursor() != Qt.CursorShape.WaitCursor

    def test_prevent_updates(self):
        """Unit test for prevent_updates"""

        assert not main_window.prevent_updates

        with self.workflows.prevent_updates():
            assert main_window.prevent_updates

        assert not main_window.prevent_updates

    def test_reset_changed_since_save(self):
        """Unit test for reset_changed_since_save"""

        main_window.settings.changed_since_save = True
        self.workflows.reset_changed_since_save()
        assert not main_window.settings.changed_since_save

    def test_insert_sum_creates_scalar_sum_formula(self):
        grid = main_window.grid
        grid.model.code_array[0, 0, 0] = "1"
        grid.model.code_array[0, 1, 0] = "2"
        grid.model.code_array[1, 0, 0] = "3"
        grid.model.code_array[1, 1, 0] = "4"

        from nxsheet.lib.selection import Selection
        selection = Selection([(0, 0)], [(1, 1)], [], [], [])
        main_window._last_focused_grid = grid
        grid.current = (3, 2, 0)
        with patch.object(type(grid), "selection", new_callable=PropertyMock,
                          return_value=selection):
            self.workflows.macro_insert_sum()

        code = grid.model.code_array[2, 1, 0]
        assert code == 10

    def test_legacy_lowercase_sum_skips_empty_cells(self):
        grid = main_window.grid
        grid.model.code_array[0, 1, 0] = "1"
        grid.model.code_array[1, 1, 0] = "2"
        grid.model.code_array[2, 1, 0] = "3"
        code = ("sum(value for value in (S[(0, 1, 0)], S[(1, 1, 0)], "
                "S[(2, 1, 0)], S[(3, 1, 0)]) if value is not None)")

        assert grid.model.code_array._eval_cell((4, 1, 0), code) == 6

    def test_export_filters_include_common_formats(self):
        """Common export formats should be available."""

        filters = [
            "CSV (*.csv)",
            "JSON (*.json)",
            "PDF (*.pdf)",
            "TXT (*.txt)",
            "HTML (*.html)",
            "XLSX (*.xlsx)",
            "XLS (*.xls)",
            "ODS (*.ods)",
            "SVG (*.svg)",
        ]

        for fmt in filters:
            assert fmt in filters

    param_update_main_window_title = [
        (Path.home(), "pyspread"),
        (Path("/test.pys"), "test.pys - pyspread"),
    ]

    @pytest.mark.parametrize("path, title", param_update_main_window_title)
    def test_update_main_window_title(self, path, title):
        """Unit test for update_main_window_title"""

        main_window.settings.last_file_input_path = path
        self.workflows.update_main_window_title()
        assert main_window.windowTitle() == title

    param_file_new = [
        ((1000, 100, 3), (1000, 100, 3), None),
        ((100, 100, 3), (100, 100, 3), None),
        ((10000000, 100, 3), (1000, 100, 3),
         "Error: Grid shape (10000000, 100, 3) exceeds (1000000, 100000, 100)."
         ),
        (None, (1000, 100, 3), None),
    ]

    @pytest.mark.parametrize("shape, res, msg", param_file_new)
    def test_file_new(self, shape, res, msg, monkeypatch):
        """Unit test for file_new"""

        monkeypatch.setattr(GridShapeDialog, "shape", shape)
        self.workflows.file_new()

        assert main_window.grid.model.shape == res
        assert main_window.grid.current == (0, 0, 0)
        assert main_window.settings.last_file_input_path == Path.home()
        assert main_window.settings.changed_since_save is False
        assert main_window.safe_mode is False
        if msg:
            assert main_window.statusBar().currentMessage() == msg

        monkeypatch.setattr(GridShapeDialog, "shape",
                            main_window.settings.shape)
        self.workflows.file_new()

    param_count_file_lines = [
        ("", 0, "counttest.txt", None),
        ("\n"*100, 100, "counttest.txt", None),
        ("Test"*100, 0, "counttest.txt", None),
        ("Test\n"*10, 10, "counttest.txt", None),
        ("Test\n"*10, None, "false_filename.txt", "Error"),
    ]

    @pytest.mark.parametrize("txt, res, filename, msg", param_count_file_lines)
    def test_count_file_lines(self, txt, res, filename, msg, tmpdir):
        """Unit test for count_file_lines"""

        tmpfile = tmpdir / "counttest.txt"
        tmpfile.write_text(txt, "utf-8")
        testfile = tmpdir / filename
        assert self.workflows.count_file_lines(testfile) == res
        if msg:
            assert str(testfile) in main_window.statusBar().currentMessage()
        tmpfile.remove()

    def test_edit_sort_ascending(self):
        """Unit test for test_edit_sort_ascending"""

        main_window.grid.model.code_array[0, 0, 0] = "1"
        main_window.grid.model.code_array[1, 0, 0] = "3"
        main_window.grid.model.code_array[2, 0, 0] = "2"
        main_window.grid.model.code_array[0, 1, 0] = "12"
        main_window.grid.model.code_array[1, 1, 0] = "33"
        main_window.grid.model.code_array[2, 1, 0] = "24"

        for row in range(3):
            for column in range(2):
                index = main_window.grid.model.index(row, column)
                main_window.grid.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.Select)

        self.workflows.edit_sort_ascending()
        assert main_window.grid.model.code_array((0, 0, 0)) == "1"
        assert main_window.grid.model.code_array((1, 0, 0)) == "2"
        assert main_window.grid.model.code_array((2, 1, 0)) == "33"

    def test_edit_sort_descending(self):
        """Unit test for test_edit_sort_descending"""

        main_window.grid.model.code_array[0, 0, 0] = "1"
        main_window.grid.model.code_array[1, 0, 0] = "3"
        main_window.grid.model.code_array[2, 0, 0] = "2"
        main_window.grid.model.code_array[0, 1, 0] = "12"
        main_window.grid.model.code_array[1, 1, 0] = "33"
        main_window.grid.model.code_array[2, 1, 0] = "24"

        for row in range(3):
            for column in range(2):
                index = main_window.grid.model.index(row, column)
                main_window.grid.selectionModel().select(
                    index, QItemSelectionModel.SelectionFlag.Select)

        self.workflows.edit_sort_descending()
        assert main_window.grid.model.code_array((0, 0, 0)) == "3"
        assert main_window.grid.model.code_array((1, 0, 0)) == "2"
        assert main_window.grid.model.code_array((2, 1, 0)) == "12"

