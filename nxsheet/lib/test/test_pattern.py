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

**Unit tests for pattern.py**

"""

from itertools import islice
import pytest
from ..pattern import count2d, enum_cycle, enum_cycle2d, pattern, pattern2d


param_test_count2d = [
    ((0, 0), 0, []),
    ((0, 0), 30,
     [(0, 0), (0, 1), (1, 1), (1, 0), (0, 2),
     (1, 2), (2, 2), (2, 0), (2, 1), (0, 3),
     (1, 3), (2, 3), (3, 3), (3, 0), (3, 1),
     (3, 2), (0, 4), (1, 4), (2, 4), (3, 4),
     (4, 4), (4, 0), (4, 1), (4, 2), (4, 3),
     (0, 5), (1, 5), (2, 5), (3, 5), (4, 5)]),
    ((2, 4), 20,
     [(2, 4), (2, 5), (3, 5), (3, 4), (2, 6), (3, 6), (4, 6), (4, 4), (4, 5),
      (2, 7), (3, 7), (4, 7), (5, 7), (5, 4), (5, 5), (5, 6), (2, 8), (3, 8),
      (4, 8), (5, 8)]),
]


@pytest.mark.parametrize("start, stop, res", param_test_count2d)
def test_count2d(start, stop, res):
    """Unit test for count2d"""

    assert list(islice(count2d(start), stop)) == res


param_test_enum_cycle = [
    ([], 0, 10, []),
    (range(5), 0, 10, [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
                       (1, 0), (1, 1), (1, 2), (1, 3), (1, 4)]),
    (['a', 'b'], 1, 6, [(1, 'a'), (1, 'b'),
                        (2, 'a'), (2, 'b'),
                        (3, 'a'), (3, 'b')]),
]


@pytest.mark.parametrize("iterable, start, stop, res", param_test_enum_cycle)
def test_enum_cycle(iterable, start, stop, res):
    """Unit test for enum_cycle"""

    assert list(islice(enum_cycle(iterable, start), stop)) == res


param_test_enum_cycle2d = [
    ([], (0, 0), 10, []),
    ([(0, 1), (1, 2)], (0, 0), 10,
     [((0, 0), (0, 1)), ((0, 0), (1, 2)), ((0, 1), (0, 1)), ((0, 1), (1, 2)),
      ((1, 1), (0, 1)), ((1, 1), (1, 2)), ((1, 0), (0, 1)), ((1, 0), (1, 2)),
      ((0, 2), (0, 1)), ((0, 2), (1, 2))]),
]


@pytest.mark.parametrize("iterable, start, stop, res", param_test_enum_cycle2d)
def test_enum_cycle2d(iterable, start, stop, res):
    """Unit test for enum_cycle2d"""

    assert list(islice(enum_cycle2d(iterable, start), stop)) == res


param_test_pattern = [
    ([1, 2, 4], 10, 22, [1, 2, 4, 11, 12, 14, 21]),
    ([0, 6, 9], 20, 29, [0, 6, 9, 20, 26]),
]


@pytest.mark.parametrize("numbers, offset, stop, res",
                         param_test_pattern)
def test_pattern(numbers, offset, stop, res):
    """Unit test for pattern"""

    assert list(pattern(numbers, offset, stop)) == res


param_test_pattern2d = [
    ([(0, 0), (1, 2)], (10, 10), (15, 15), (None, None), None,
     [(0, 0), (1, 2), (10, 0), (11, 2), (0, 10), (1, 12), (10, 10), (11, 12)]),
    ([(0, 1), (2, 2), (4, 2)], (10, 10), (10, 10), (None, None), None,
     [(0, 1), (2, 2), (4, 2)]),
    ([(0, 1), (2, 2), (4, 2)], (10, 10), (20, 20), (None, None), None,
     [(0, 1), (2, 2), (4, 2), (10, 1), (12, 2), (14, 2), (0, 11),
      (2, 12), (4, 12), (10, 11), (12, 12), (14, 12)]),
    ([(0, 1), (2, 2), (4, 2)], (5, 10), (10, 10), (None, None), None,
     [(0, 1), (2, 2), (4, 2), (5, 1), (7, 2), (9, 2)]),
    ([(0, 1), (2, 2), (4, 2)], (10, 5), (10, 10), (None, None), None,
     [(0, 1), (2, 2), (4, 2), (0, 6), (2, 7), (4, 7)]),
    ([(14, 2)], (1, 1), (24, 6), (None, None), None,
     [(14, 2), (14, 3), (14, 4), (14, 5), (15, 2), (15, 3), (15, 4), (15, 5),
      (16, 2), (16, 3), (16, 4), (16, 5), (17, 2), (17, 3), (17, 4), (17, 5),
      (18, 2), (18, 3), (18, 4), (18, 5), (19, 2), (19, 3), (19, 4), (19, 5),
      (20, 2), (20, 3), (20, 4), (20, 5), (21, 2), (21, 3), (21, 4), (21, 5),
      (22, 2), (22, 3), (22, 4), (22, 5), (23, 2), (23, 3), (23, 4), (23, 5)]),
    ([(14, 2)], (10, 10), (10, 10), (5, 5), None, []),
]


@pytest.mark.parametrize("tuples, offset, stop, limit, only, res",
                         param_test_pattern2d)
def test_pattern2d(tuples, offset, stop, limit, only, res):
    """Unit test for pattern2d"""

    assert sorted(list(pattern2d(tuples, offset, stop,
                                 limit, only))) == sorted(res)
