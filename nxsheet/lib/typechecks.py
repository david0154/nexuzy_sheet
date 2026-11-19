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

Functions for checking types and type likeness

**Provides**

 * :func:`is_stringlike`
 * :func:`is_svg`
 * :func:`check_shape_validity`

"""

from io import BytesIO
import xml.etree.ElementTree as ET
from typing import Tuple


def is_stringlike(obj: object) -> bool:
    """Is `obj` string like

    :param obj: Object to be checked
    :return: True if obj is instance of str, bytes or bytearray

    """

    return isinstance(obj, (str, bytes, bytearray))


def is_svg(svg_bytes: bytes) -> bool:
    """Checks if svg_bytes is an svg image

    :param svg_bytes: Data to be checked for being an SVG image
    :return: True if svg_bytes seems to be an  SVG image

    """

    tag = None

    with BytesIO(svg_bytes) as svg:
        try:
            for event, el in ET.iterparse(svg, ('start',)):
                tag = el.tag
                break
        except ET.ParseError:
            pass

    return tag == '{http://www.w3.org/2000/svg}svg'


def check_shape_validity(shape: Tuple[int, int, int],
                         maxshape: Tuple[int, int, int]) -> bool:
    """Checks if shape is valid

    :param shape: shape for grid to be checked
    :param maxshape: maximum shape for grid
    :return: True if yes, raises a ValueError otherwise

    """

    try:
        iter(shape)
    except TypeError:
        # not iterable
        raise ValueError("{} is not iterable".format(shape))

    try:
        if len(shape) != 3:
            raise ValueError("len({}) != 3".format(shape))
    except TypeError:
        # no length
        raise ValueError("{} has no length".format(shape))

    if any(ax == 0 for ax in shape):
        raise ValueError("Elements {} equals 0".format(shape))

    if any(ax > axmax for axmax, ax in zip(maxshape, shape)):
        raise ValueError("Grid shape {} exceeds {}.".format(shape, maxshape))

    return True
