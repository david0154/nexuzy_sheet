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

 * :class:`ProgressDialogCanceled`
 * :func:`progress_dialog`
 * :func:`linecount`
 * :func:`file_progress_gen`

"""

from contextlib import contextmanager
from functools import partial
from typing import BinaryIO, ContextManager, Generator, IO, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QProgressDialog


class ProgressDialogCanceled(Exception):
    """Raised when a progress dialog is canceled"""

    pass


@contextmanager
def progress_dialog(main_window: QMainWindow, title: str, label: str,
                    maximum: int) -> ContextManager[QProgressDialog]:
    """:class:`~contextlib.contextmanager` that displays a progress dialog

    :param main_window: Application main window
    :param title: Progress dialog title
    :param label: Progress dialog label
    :param maximum: Maximum value for progress

    """

    progress_dialog = QProgressDialog(main_window)
    progress_dialog.setWindowTitle(title)
    progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
    progress_dialog.setLabelText(label)
    progress_dialog.setMaximum(maximum)

    yield progress_dialog

    progress_dialog.setValue(maximum)
    progress_dialog.close()
    progress_dialog.deleteLater()


def linecount(infile: BinaryIO, buffer_size: int = 1024*1024) -> int:
    """Count lines in infile

    Starts at current position in file. Position is not preserved.
    Idea taken from https://stackoverflow.com/questions/845058

    :param infile: File like object for which lines are counted (binary mode!)
    :param buffer_size: Buffer size for reading the file
    :return: Number of newlines in infile

    """

    buffer_gen = iter(partial(infile.raw.read, buffer_size), b'')
    return sum(buffer.count(b'\n') for buffer in buffer_gen)


def file_progress_gen(main_window, file: IO, title: str, label: str,
                      no_lines: int, step: int = 100) \
                      -> Generator[Tuple[int, str], None, None]:
    """A generator for file iteration that displays a progress bar

    Yields (line number, line string).
    Return value on user cancel via progress dialog is current line number

    :param main_window: Application main window
    :param file: File to be iterater over
    :param title: Progress dialog title
    :param label: Progress dialog label
    :param no_lines: Number of lines that are remaining in file
    :param step: Number of lines per progress bar update

    """

    with progress_dialog(main_window, title, label, no_lines) as progress_dlg:
        try:
            for i, line in enumerate(file):
                yield i, line

                if not i % step:
                    progress_dlg.setValue(i)
                    QApplication.instance().processEvents()
                    if progress_dlg.wasCanceled():
                        msg = "File operation canceled at line {}.".format(i)
                        raise ProgressDialogCanceled(msg)
        except GeneratorExit:  # Catch for cleaning up with progress_dialog
            pass
        except ProgressDialogCanceled:
            raise
        except Exception as error:
            main_window.grid.model.reset()
            main_window.statusBar().showMessage(str(error))
