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

High resolution svg support for qimage and :mod:`matplotlib.figure`

**Provides**

* :class:`QImageSvg`


"""

from io import StringIO

from PyQt6.QtGui import QImage, QPainter
try:
    from PyQt6.QtSvg import QSvgRenderer
except ImportError:
    QSvgRenderer = None

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
except ImportError:
    Figure = None


class QImageSvg(QImage):
    """Subclass of PyQt6.QtGui

    Adds support for SVG byte strings and matplotlib figures

    """

    def from_svg_bytes(self, svg_bytes: bytes):
        """Paints an svg from a bytes object

        :param svg_bytes: SVG file content

        """

        renderer = QSvgRenderer(svg_bytes)
        painter = QPainter(self)
        painter.eraseRect(self.rect())
        renderer.render(painter)
        painter.end()

    def _matplotlib_figure2svg_bytes(self, figure: Figure) -> bytes:
        """Converts a a matplotlib figure to an SVG bytes object

        :param figure: Matplotib figure
        :return: SVG file content

        """

        canvas = FigureCanvasQTAgg(figure)
        svg_filelike = StringIO()
        figure.savefig(svg_filelike, format="svg")
        svg_filelike.seek(0)
        svg_bytes = bytes(svg_filelike.read(), encoding='utf-8')
        svg_filelike.close()

        return svg_bytes

    def from_matplotlib(self, figure: Figure):
        """Paints an svg from a matplotlib figure

        :param figure: Matplotib figure

        """

        if not isinstance(figure, Figure):
            msg_tpl = "figure must be instance of {}."
            msg = msg_tpl.format(Figure)
            raise ValueError(msg)

        svg_bytes = self._matplotlib_figure2svg_bytes(figure)
        self.from_svg_bytes(svg_bytes)
