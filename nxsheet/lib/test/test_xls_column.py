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

Tests for `xlsx.py`

"""

from contextlib import contextmanager
from pathlib import Path
import pytest
import sys

ORIGIN_PATH = Path(__file__).parent.parent.parent


@contextmanager
def insert_path(path):
    sys.path.insert(0, path)
    yield
    sys.path.pop(0)


with insert_path(ORIGIN_PATH):
    from lib.xls_column import xls_column


test_params_excel_column = (
    (0, "A"),
    (1, "B"),
    (2, "C"),
    (23, "X"),
    (24, "Y"),
    (25, "Z"),
    (26, "AA"),
    (52, "BA"),
    (650, "YA"),
    (651, "YB"),
    (701, "ZZ"),
    (702, "AAA"),
    (703, "AAB"),
    (16383, "XFD"),
    (18277, "ZZZ"),
    (475253, "ZZZZ"),
    (2**100+1, "BKOWAWZZAERONYJCMBBOJR"),
)


@pytest.mark.parametrize("column, result", test_params_excel_column)
def test_excel_column(column, result):
    """pytest for `excel_column`"""

    assert xls_column(column) == result


def test_xls_column_error_message():
    """Test that error message is correctly formatted."""

    column = -2

    with pytest.raises(ValueError) as exc_info:
        xls_column(column)
    assert str(exc_info.value) == f"Column number {column} is negative."
