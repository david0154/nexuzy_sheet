#!/usr/bin/python3
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

Nexuzy Sheet
============

- Excel-like Python spreadsheet application
- Run this script to start the application.

**Provides**

* MainApplication: Initial command line operations and application launch
* :class:`MainWindow`: Main windows class

"""

import logging
import os
import sys
import traceback

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

try:
    from nxsheet.cli import PyspreadArgumentParser
    from nxsheet.main_window import MainWindow

except ImportError:
    from cli import PyspreadArgumentParser
    from main_window import MainWindow


LICENSE = "MIT License"

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"


def excepthook(exception_type, exception_value, exception_traceback):
    """Exception hook that prevents Nexuzy Sheet from crashing"""

    traceback_msg = "".join(traceback.format_exception(exception_type,
                                                       exception_value,
                                                       exception_traceback))
    print(f"Error: {traceback_msg}\n")


def main():
    """Nexuzy Sheet main"""

    sys.excepthook = excepthook

    parser = PyspreadArgumentParser()
    args, _ = parser.parse_known_args()

    logging.basicConfig(level=args.loglevel)

    app = QApplication(sys.argv)
    app.setApplicationName("Nexuzy Sheet")
    app.setDesktopFileName("io.nexuzy.nexuzysheet")
    app.setOrganizationName("Nexuzy Lab")

    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "io.nexuzy.nexuzysheet")
        except (AttributeError, OSError):
            pass

    try:
        from nxsheet.icons import Icon
    except ImportError:
        from icons import Icon

    app_icon = Icon.app_ico if sys.platform.startswith("win") else Icon.app
    app.setWindowIcon(app_icon)
    main_window = MainWindow(args.file, default_settings=args.default_settings)
    main_window.setWindowIcon(app_icon)

    main_window.show()

    app.exec()

    sys.exit()


if __name__ == '__main__':
    main()

