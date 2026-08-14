#!/usr/bin/env python
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

Tools for converting Excel style column names

**Provides**

 * :func:`xls_column`


"""


def xls_column(column: int) -> str:
    """Converts column number to Excel like column name in A, B, C notation

    The Excel like notationis created for arbitrary numbers.
    Limitations of Excel implementations are not taken into account.

    :param column: Column number starting with 0
    :return: String with Excel like column

    """

    if column < 0:
        raise ValueError(f"Column number {column} is negative.")

    start_char = 65
    base = 26

    result = []
    while column >= 0:
        column, remainder = divmod(column, base)
        result.append(chr(start_char + remainder))
        column -= 1

    return "".join(reversed(result))
