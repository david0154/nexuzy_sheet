# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet AI Integration
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
# Developer AI Integration
# Lightweight AI components: Qwen3, PaddleOCR, OpenCV, PyMuPDF
# Local execution, no cloud APIs, no unnecessary large models

"""
Nexuzy Sheet AI Integration

Four core components:
- Qwen3-0.6B (GGUF Q4 via llama.cpp): text/reasoning, formula generation
- PaddleOCR PP-OCRv6 Tiny: document/image text recognition
- OpenCV: image preprocessing (deskew, crop, noise removal, etc)
- PyMuPDF: PDF text/page extraction

All components run locally. No cloud APIs.
"""

from .coordinator import AICoordinator
from .schemas import AIAction, AIActionType

__all__ = [
    'AICoordinator',
    'AIAction',
    'AIActionType',
]
