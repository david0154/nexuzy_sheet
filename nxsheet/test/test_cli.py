# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Developed by Nexuzy Lab
#
# Nexuzy Sheet is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Nexuzy Sheet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# License: GNU General Public License v3.0
# https://www.gnu.org/licenses/gpl-3.0.html
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
