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

**Provides**

 * :func:`quote`
 * :func:`wrap_text`

"""

import textwrap

ZEN = """The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
"""


def quote(code: str) -> str:
    """Quote code

    :param code: Code to be quoted
    :return: Quoted code if not already quoted and quoting possible

    """

    starts_and_ends = [
        ("'", "'"),
        ('"', '"'),
        ("u'", "'"),
        ('u"', '"'),
        ("b'", "'"),
        ('b"', '"'),
        ("r'", "'"),
        ('r"', '"'),
    ]

    if code is None or not (isinstance(code, bytes) or isinstance(code, str)):
        return code

    code = code.strip()

    if code and not (code[0],  code[-1]) in starts_and_ends:
        return repr(code)
    else:
        return code


def wrap_text(text, width=80, maxlen=2000):
    """Wrap text to line width

    :param text: The text to be wrapped
    :param width: Width of the text to be wrapped
    :param maxlen: Maximum total text length before text in truncated and
                   extended by [...]. If None then truncation is disabled.
    :return: Wrapped text

    """

    if text is None:
        return

    if maxlen is not None and len(text) > maxlen:
        text = text[:maxlen] + "..."
    return "\n".join(textwrap.wrap(text, width=width))
