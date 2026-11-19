# -*- coding: utf-8 -*-

# Copyright Martin Manns
# Copyright Seongyong Park
# Distributed under the terms of the MIT License

# --------------------------------------------------------------------
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

"""
parsers
=======

Provides parsers to apply on expressions that are not pure Python expressions

Provides
--------

* spreadsheet_formula_to_code: Spreadsheet formula parser

"""

try:
    import pycel
    from pycel import excelformula
except ImportError:
    pycel = None


def spreadsheet_formula_to_code(formula: str) -> str:
    """ Converts spreadsheet formula into Python code via pycel """
    if pycel is None:
        return formula

    ex = excelformula.ExcelFormula(formula)
    return ex.python_code
