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

**Unit tests for string_helpers.py**

"""

import pytest
from ..string_helpers import quote, wrap_text


param_test_quote = [
    (None, None),
    (1, 1),
    ("", ""),
    ("Test", "'Test'"),
    ("ü+", "'ü+'"),
    (u"ü+", "'ü+'"),
    (r"ü+", "'ü+'"),
    (b"Test", "b'Test'"),
    ("Test1\nTest2", "'Test1\\nTest2'"),
]


@pytest.mark.parametrize("code, res", param_test_quote)
def test_quote(code, res):
    """Unit test for quote"""

    assert quote(code) == res


param_test_wrap_text = [
    ("", 80, 2000, ""),
    ("."*81, 80, 2000, "."*80+"\n."),
    (r"."*81, 80, 2000, "."*80+"\n."),
    ("~"*81, 80, 2000, "~"*80+"\n~"),
    (u"\u2200"*81, 80, 2000, "\u2200"*80+"\n\u2200"),
    ("."*160, 80, 2000, "."*80+"\n"+"."*80),
    ("x"*160, 80, 2, "xx..."),
    ("."*10, 2, 2000, "\n".join([".."]*5)),
    (None, 2, 10, None)
]


@pytest.mark.parametrize("text, width, maxlen, res", param_test_wrap_text)
def test_wrap_text(text, width, maxlen, res):
    """Unit test for wrap_text"""

    assert wrap_text(text, width, maxlen) == res
