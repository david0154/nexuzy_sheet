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

**Unit tests for file_helpers.py**

"""

import pytest
from ..file_helpers import linecount


param_test_linecount = [
    (b"", 0),
    (b"\n", 1),
    (b"Test1\nTest2", 1),
    (b"Test1\nTest2\n", 2),
    (b" \n" * 1000, 1000),
    (b"\n" * 2**20, 2**20),
]


@pytest.mark.parametrize("content, res", param_test_linecount)
def test_linecount(content, res, tmp_path):
    """Unit test for linecount"""

    testfile_path = tmp_path / "test"
    testfile_path.write_bytes(content)
    with open(testfile_path, "rb") as testfile:
        assert linecount(testfile) == res
