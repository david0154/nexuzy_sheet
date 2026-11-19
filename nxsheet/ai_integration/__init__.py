# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet AI Integration
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
# Developer AI Integration
# Lightweight AI components: Qwen2.5, PaddleOCR, OpenCV, PyMuPDF
# Local execution, no cloud APIs, no unnecessary large models

"""
Nexuzy Sheet AI Integration

Four core components:
- Qwen2.5-0.5B-Instruct (GGUF Q4_K_M via llama.cpp): text/reasoning, formulas
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
