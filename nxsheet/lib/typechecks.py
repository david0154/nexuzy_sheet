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
