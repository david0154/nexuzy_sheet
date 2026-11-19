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
test_grid_renderer
==================

Unit tests for grid_renderer.py

"""

from contextlib import contextmanager
from os.path import abspath, dirname, join
import sys

import pytest

from PyQt6.QtWidgets import QApplication

PYSPREADPATH = abspath(join(dirname(__file__) + "/.."))
LIBPATH = abspath(PYSPREADPATH + "/lib")


@contextmanager
def insert_path(path):
    sys.path.insert(0, path)
    yield
    sys.path.pop(0)


with insert_path(PYSPREADPATH):
    from ..main_window import MainWindow
    from ..grid_renderer import GridCellNavigator

app = QApplication.instance()
if app is None:
    app = QApplication([])
main_window = MainWindow()


class TestGridCellNavigator:
    """Unit tests for GridCellNavigator in grid_renderer.py"""

    grid = main_window.grid

    param_test_above_keys = [
        ((0, 0, 0), [(-1, 0, 0)]),
        ((20, 0, 0), [(19, 0, 0)]),
        ((20, 0, 2), [(19, 0, 2)]),
        ((20, 2, 2), [(19, 2, 2)]),
    ]

    @pytest.mark.parametrize("key, res", param_test_above_keys)
    def test_above_keys(self, key, res):
        """Unit test for above_keys"""

        cell = GridCellNavigator(self.grid, key)
        assert set(cell.above_keys()) == set(res)

    param_test_below_keys = [
        ((0, 0, 0), [(1, 0, 0)]),
        ((1000, 0, 0), [(1001, 0, 0)]),
        ((20, 0, 2), [(21, 0, 2)]),
        ((20, 2, 2), [(21, 2, 2)]),
    ]

    @pytest.mark.parametrize("key, res", param_test_below_keys)
    def test_below_keys(self, key, res):
        """Unit test for below_keys"""

        cell = GridCellNavigator(self.grid, key)
        assert set(cell.below_keys()) == set(res)

    param_test_left_keys = [
        ((0, 0, 0), [(0, -1, 0)]),
        ((20, 0, 0), [(20, -1, 0)]),
        ((20, 0, 2), [(20, -1, 2)]),
        ((20, 2, 2), [(20, 1, 2)]),
    ]

    @pytest.mark.parametrize("key, res", param_test_left_keys)
    def test_left_keys(self, key, res):
        """Unit test for left_keys"""

        cell = GridCellNavigator(self.grid, key)
        assert set(cell.left_keys()) == set(res)

    param_test_right_keys = [
        ((0, 0, 0), [(0, 1, 0)]),
        ((20, 0, 0), [(20, 1, 0)]),
        ((20, 0, 2), [(20, 1, 2)]),
        ((20, 2, 2), [(20, 3, 2)]),
    ]

    @pytest.mark.parametrize("key, res", param_test_right_keys)
    def test_right_keys(self, key, res):
        """Unit test for right_keys"""

        cell = GridCellNavigator(self.grid, key)
        assert set(cell.right_keys()) == set(res)

    param_test_above_left_key = [
        ((0, 0, 0), (-1, -1, 0)),
        ((20, 0, 0), (19, -1, 0)),
        ((20, 0, 2), (19, -1, 2)),
        ((20, 2, 2), (19, 1, 2)),
    ]

    @pytest.mark.parametrize("key, res", param_test_above_left_key)
    def test_above_left_key(self, key, res):
        """Unit test for above_left_key"""

        cell = GridCellNavigator(self.grid, key)
        assert cell.above_left_key() == res

    param_test_above_right_key = [
        ((0, 0, 0), (-1, 1, 0)),
        ((20, 0, 0), (19, 1, 0)),
        ((20, 0, 2), (19, 1, 2)),
        ((20, 2, 2), (19, 3, 2)),
    ]

    @pytest.mark.parametrize("key, res", param_test_above_right_key)
    def test_above_right_key(self, key, res):
        """Unit test for above_right_key"""

        cell = GridCellNavigator(self.grid, key)
        assert cell.above_right_key() == res

    param_test_below_left_key = [
        ((0, 0, 0), (1, -1, 0)),
        ((20, 0, 0), (21, -1, 0)),
        ((20, 0, 2), (21, -1, 2)),
        ((20, 2, 2), (21, 1, 2)),
    ]

    @pytest.mark.parametrize("key, res", param_test_below_left_key)
    def test_below_left_key(self, key, res):
        """Unit test for below_left_key"""

        cell = GridCellNavigator(self.grid, key)
        assert cell.below_left_key() == res

    param_test_below_right_key = [
        ((0, 0, 0), (1, 1, 0)),
        ((20, 0, 0), (21, 1, 0)),
        ((20, 0, 2), (21, 1, 2)),
        ((20, 2, 2), (21, 3, 2)),
    ]

    @pytest.mark.parametrize("key, res", param_test_below_right_key)
    def test_below_right_key(self, key, res):
        """Unit test for below_right_key"""

        cell = GridCellNavigator(self.grid, key)
        assert cell.below_right_key() == res
