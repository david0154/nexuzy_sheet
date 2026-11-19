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
test_cli
========

Unit tests for cli.py

"""

from argparse import Namespace
from contextlib import contextmanager
from os.path import abspath, dirname, join
import sys
from unittest.mock import patch
from pathlib import Path, PosixPath

import pytest

PYSPREADPATH = abspath(join(dirname(__file__) + "/.."))
LIBPATH = abspath(PYSPREADPATH + "/lib")


@contextmanager
def insert_path(path):
    sys.path.insert(0, path)
    yield
    sys.path.pop(0)


with insert_path(PYSPREADPATH):
    from ..cli import PyspreadArgumentParser

param_test_cli = [
    (['pyspread'],
     Namespace(file=None, default_settings=False, loglevel=30)),
    (['pyspread', 'test.pys'],
     Namespace(file=PosixPath("test.pys"), default_settings=False,
               loglevel=30)),
    (['pyspread', '--help'],
     None),
    (['pyspread', '--version'],
     None),
    (['pyspread', '--default-settings'],
     Namespace(file=None, default_settings=True, loglevel=30)),
    (['pyspread', '-d'],
     Namespace(file=None, default_settings=False, loglevel=10)),
    (['pyspread', '-v'],
     Namespace(file=None, default_settings=False, loglevel=20)),
]


@pytest.mark.parametrize("argv, res", param_test_cli)
def test_cli(argv, res):
    with patch('argparse._sys.argv', argv):
        parser = PyspreadArgumentParser()
        if res is None:
            with pytest.raises(SystemExit) as exc:
                args, unknown = parser.parse_known_args()
            assert exc.value.code == 0
        else:
            args, unknown = parser.parse_known_args()
            assert args == res
