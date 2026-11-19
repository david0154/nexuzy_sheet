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
test_hashing
============

Unit tests for hashing.py

"""

import pytest
from ..hashing import genkey, sign, verify


KEYS = [genkey() for _ in range(100)]


def test_genkey():
    """Unit test for genkey"""

    keys = []

    for length in range(1, 65):
        keys.append(genkey(length))

    for i, key in enumerate(keys):
        assert len(key) == i + 1

    assert len(set(KEYS)) == len(KEYS)

    with pytest.raises(ValueError):
        genkey(65)


param_test_sign = [
    ("", None, "", ValueError),
    ("2", "123", b"", TypeError),
    (b"2", b"123", b"287715fdf85b987e2bc3f468b4a53346aee8da24305ff4456dd3390c"
                   b"7ab5a7cdf5f5dbb6831310880909aedfd21e59f1b7c4421482a33b3"
                   b"450c38ffcbf1bf11e", None),
    ("2", "123", b"", TypeError),
    (b"2", 123, "", ValueError),
    (b"2", b"1"*1000, b"", UserWarning),
]


@pytest.mark.parametrize("data, key, res, error", param_test_sign)
def test_sign(data, key, res, error):
    """Unit test for sign"""
    if error and issubclass(error, Exception):
        with pytest.raises(error):
            sign(data, key)
    elif error and issubclass(error, UserWarning):
        with pytest.warns(error):
            sign(data, key)
    else:
        assert sign(data, key) == res


param_test_sign_verify = [
    (b"Test", KEYS[0], b"Test", KEYS[0], True),
    (100*"\u2200".encode('utf-8'), KEYS[0], 100*"\u2200".encode('utf-8'),
     KEYS[0], True),
    (b"Test", KEYS[0], b"Test", KEYS[1], False),
    (b"Test", KEYS[0], b"TEST", KEYS[0], False),
    (b"Test", KEYS[0], b"TEST", KEYS[3], False),
    (b"", KEYS[0], b"", KEYS[3], ValueError),
    (b"", KEYS[0], b"", KEYS[0], ValueError),
    (b"Hello World\n"*10, KEYS[1], b"Hello World\n"*10, KEYS[1], True),
]


@pytest.mark.parametrize("data1, sigkey, data2, verkey, res",
                         param_test_sign_verify)
def test_sign_verify(data1, sigkey, data2, verkey, res):
    """Unit test for sign and verify"""

    if res is ValueError:
        with pytest.raises(res):
            sign(data1, sigkey)
    else:
        signature = sign(data1, sigkey)
        verify(data2, signature, verkey)
        assert verify(data2, signature, verkey) == res
