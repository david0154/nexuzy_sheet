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

Pattern
-------


**Provides**

* :func:`enum_cycle`: Cycle with cycle count

"""

from itertools import count
from typing import Generator, Tuple


def count2d(start: Tuple[int, int] = (0, 0)) -> Generator[Tuple[int, int]]:
    """Generates tuples that cover an infinite grid with indices

    :param start: Start row and column values for counting
    """

    start_row, start_column = start

    for grid_size in count():
        # Yield the last row
        for row in range(grid_size + 1):
            yield start_row + row, start_column + grid_size

        # Yield the last column excluding the corner
        for column in range(grid_size):
            yield start_row + grid_size, start_column + column


def enum_cycle(iterable: iter, start: int = 0) -> Generator[Tuple[int, any]]:
    """Cycle with cycle count

    Behaves like cycle but yields tuples `<cycle number>, <value>`

    :param iterable: Iterable to be cycles over, stored in memory as a tuple
    :param start: Start value for counting

    """

    elements = tuple(iterable)

    while elements:
        for i in count(start):
            for element in elements:
                yield i, element


def enum_cycle2d(iterable: iter, start: Tuple[int, int] = (0, 0)) \
     -> Generator[Tuple[int, any]]:
    """2D cycle with cycle count

    Behaves like cycle but yields tuples `<cycle number>, <value>`

    :param iterable: Iterable of 2-tuples to be cycles over, stored in memory
    :param start: Start value for counting

    """

    elements = tuple(iterable)

    while elements:
        for cycle_row, cycle_column in count2d(start):
            for element in elements:
                yield (cycle_row, cycle_column), element


def pattern(numbers: iter, offset: int, stop: int = None) -> Generator[int]:
    """Generates a number pattern repeating each time adding an offset

    The pattern is filled with growing numbers, where the offset is added
    to the result once for each cycle.

    :param numbers: Iterable of numbers
    :param offset: Offset to be added for each cycle
    :param stop: Generator stops before reaching the stop value

    """

    if not offset:
        raise ValueError("Offset must not be 0.")

    for i, number in enum_cycle(numbers):
        value = number + i * offset
        if value >= stop:
            break
        yield value


def pattern2d(tuples: iter, offset: Tuple[int, int],
              stop: Tuple[int, int],
              limit: Tuple[int, int] = (None, None),
              only: list = None,
              cycle_log: list = None) -> Generator[Tuple[int, int]]:
    """Generates a 2D number pattern

    The pattern repeats itself first in the row and column direction
    as well as diagonally, each time adding row and column offsets.

    The pattern is filled with growing numbers, where the offset is added
    to the result once for each cycle.

    :param tuples: Iterable of numbers
    :param offset: Offset to be added for each cycle
    :param stop: Generator stops before reaching the stop values
    :param limit: Generator lowers all values greater than max to max
    :param only: If given only the provided indices are yielded
    :param cycle_log: Mutated to log all yielded `(cycle_row, cycle_column)`

    """

    if not all(offset):
        raise ValueError(f"Offsets {offset} contain zeros.")

    row_offset, column_offset = offset
    row_stop, column_stop = stop
    limit_row, limit_column = limit

    cycle_log = [] if cycle_log is None else cycle_log

    apply_row_limit = limit_row is not None
    apply_col_limit = limit_column is not None

    only_set = None if only is None else set(only)

    for ((cycle_row, cycle_column),
         (row_number, column_number)) in enum_cycle2d(tuples):

        row = row_number + cycle_row * row_offset
        column = column_number + cycle_column * column_offset

        if row >= row_stop and column >= column_stop:
            return

        if row < row_stop and column < column_stop:
            if only_set is None or (cycle_row, cycle_column) in only_set:
                __row = min(row, limit_row - 1) if apply_row_limit else row
                __column = min(column,
                               limit_column - 1) if apply_col_limit else column
                yield __row, __column
                cycle_log.append((cycle_row, cycle_column))
