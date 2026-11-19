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

* :func:`check_mandatory_dependencies`:
* :class:`PathAction`:
* :class:`CommandLineParser`:

"""

from argparse import ArgumentParser
from pathlib import Path
import logging
import sys

try:
    import PyQt6.QtSvg as pyqtsvg
except ImportError:
    pyqtsvg = None

try:
    from nxsheet.__init__ import APP_NAME, VERSION
    from nxsheet.installer import REQUIRED_DEPENDENCIES
except ImportError:
    from __init__ import APP_NAME, VERSION
    from installer import REQUIRED_DEPENDENCIES


def check_mandatory_dependencies():
    """Checks mandatory dependencies and exits if they are not met"""

    def dependency_warning(message: str):
        """Print warning message to stdout

        :param message: Warning message to be displayed

        """

        sys.stdout.write(f'Warning: {message}\n')

    # Check Python version
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro
    if major < 3 or major == 3 and minor < 6:
        msg = f"Python has version {major}.{minor}.{micro}" + \
               " but ≥ 3.6 is required."
        dependency_warning(msg)

    for module in REQUIRED_DEPENDENCIES:
        if module.is_installed() is None or not module.is_installed():
            dependency_warning(f"Required module {module.name} not found.")
        elif module.version < module.required_version:
            msg = f"Module {module.name} has version {module.version}" + \
                  f"but {module.required_version} is required."
            dependency_warning(msg)
    if pyqtsvg is None:
        # Import of mandatory module failed
        msg = "Required module PyQt6.QtSvg not found."
        dependency_warning(msg)


class PyspreadArgumentParser(ArgumentParser):
    """Parser for the command line"""

    def __init__(self):
        check_mandatory_dependencies()

        description = "Nexuzy Sheet is a non-traditional spreadsheet that is " \
                      "based on and written in the programming language " \
                      "Python."

        super().__init__(prog=APP_NAME, description=description)

        self.add_argument('--version', action='version', version=VERSION)

        self.add_argument('--default-settings', action='store_true',
                          help='start with default settings and save them on '
                               'exit')

        self.add_argument('-d', '--debug',
                          help="Print debug information",
                          action="store_const", dest="loglevel",
                          const=logging.DEBUG, default=logging.WARNING)

        self.add_argument('-v', '--verbose',
                          help="Print verbose information",
                          action="store_const", dest="loglevel",
                          const=logging.INFO)

        self.add_argument('file', type=Path, nargs='?', default=None,
                          help='open a Nexuzy Sheet workbook '
                               '(.nix, .nxl or .nxs)')

