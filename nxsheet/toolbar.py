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

* :class:`ChartTemplatesToolBar`
* :class:`FindToolbar`
* :class:`FormatToolbar`
* :class:`MacroToolbar`
* :func:`add_toolbutton_widget`

"""

import os
import shutil
from typing import Tuple

from PyQt6.QtWidgets import (
        QToolBar, QToolButton, QMenu, QWidget, QHBoxLayout, QUndoView,
        QMainWindow)

try:
    import matplotlib.figure as matplotlib_figure
except ImportError:
    matplotlib_figure = None

rpy2 = None
try:
    r_home = os.environ.get("R_HOME")
    if r_home:
        os.environ["R_HOME"] = r_home
    has_r = bool(shutil.which("R")) or bool(shutil.which("Rscript"))
    if has_r:
        import rpy2
        from rpy2.robjects.packages import importr, PackageNotInstalledError
except Exception:
    rpy2 = None

try:
    import plotnine
except ImportError:
    plotnine = None

try:
    from nxsheet.actions import MainWindowActions, ChartDialogActions
    from nxsheet.icons import Icon
    from nxsheet.menus import ToolbarManagerMenu
    from nxsheet.widgets import FindEditor
except ImportError:
    from actions import MainWindowActions, ChartDialogActions
    from icons import Icon
    from menus import ToolbarManagerMenu
    from widgets import FindEditor


def add_toolbutton_widget(button: QWidget, widget: QWidget,
                          minsize: Tuple[int, int] = (300, 200),
                          popup_mode: QToolButton.ToolButtonPopupMode
                          = QToolButton.ToolButtonPopupMode.MenuButtonPopup):
    """Adds a widget as menu to a tool_button

    :param button: Tool button for menu
    :param widget: Toolbar widget
    :param minsize: Minimum menu size
    :param popup_mode: Describes how the menu is popped up

    """

    button.setPopupMode(popup_mode)
    menu = QMenu(button)
    menu.setMinimumSize(*minsize)
    button.setMenu(menu)
    menu_layout = QHBoxLayout()
    menu_layout.addWidget(widget)
    menu.setLayout(menu_layout)
    menu.layout()


class ToolBarBase(QToolBar):
    """Base toolbar class that provides toolbar manager button method"""

    def __init__(self, title, parent, *args, **kwargs):
        super().__init__(title, parent, *args, **kwargs)

    def add_widget(self, widget: QWidget):
        """Adds widget with addWidget and assigns action text and icon

        The widget must have a label attribute and an icon method.

        :param widget: Widget to be added

        """

        self.addWidget(widget)
        self.actions()[-1].setText(widget.label)
        self.actions()[-1].setIcon(widget.icon())

    def get_manager_button(self) -> QToolButton:
        """Returns QToolButton for managing the toolbar"""

        button = QToolButton(self)
        button.setText("Add/remove toolbar icons")
        button.setMenu(ToolbarManagerMenu(self))
        button.setIcon(Icon.menu_manager)
        button.setFixedWidth(int(button.height()/3))
        button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        return button


class MainToolBar(ToolBarBase):
    """The main toolbar"""

    def __init__(self, main_window: QMainWindow):
        """
        :param main_window: Application main window

        """

        self.main_window = main_window
        super().__init__("Main toolbar", main_window)

        self.setObjectName("Main Toolbar")
        self._create_toolbar(main_window.main_window_toolbar_actions)

    def _create_toolbar(self, actions: MainWindowActions):
        """Fills the main toolbar with QActions

        :param actions: Main window actions

        """

        self.addAction(actions.new)
        self.addAction(actions.open)
        self.addAction(actions.save)
        self.addAction(actions.export)

        self.addSeparator()

        self.addAction(actions.print)

        self.addSeparator()

        self.addAction(actions.undo)
        undo_button = self.widgetForAction(actions.undo)
        undo_view = QUndoView(self.main_window.undo_stack)
        add_toolbutton_widget(undo_button, undo_view)

        self.addAction(actions.redo)

        self.addSeparator()

        self.addAction(actions.cut)
        self.addAction(actions.copy)
        self.addAction(actions.copy_results)
        self.addAction(actions.paste)
        self.addAction(actions.paste)

        self.addSeparator()

        self.addAction(actions.clone_formatting)

        self.addSeparator()

        self.addAction(actions.sort_ascending)
        self.addAction(actions.sort_descending)

        self.addSeparator()

        self.addAction(actions.toggle_spell_checker)

        self.addWidget(self.get_manager_button())


class MacroToolbar(ToolBarBase):
    """The macro toolbar for Nexuzy Sheet"""

    def __init__(self, main_window: QMainWindow):
        """
        :param main_window: Application main window

        """

        super().__init__("Macro toolbar", main_window)

        self.setObjectName("Macro toolbar")
        self._create_toolbar(main_window.main_window_toolbar_actions)

    def _create_toolbar(self, actions: MainWindowActions):
        """Fills the macro toolbar with QActions

        :param actions: Main window actions

        """

        self.addAction(actions.insert_image)
        if matplotlib_figure is not None:
            self.addAction(actions.insert_chart)

        self.addSeparator()

        self.addAction(actions.insert_sum)

        self.addWidget(self.get_manager_button())


class FindToolbar(ToolBarBase):
    """The find toolbar for Nexuzy Sheet"""

    def __init__(self, main_window: QMainWindow):
        """
        :param main_window: Application main window

        """

        super().__init__("Find Toolbar", main_window)

        self.main_window = main_window
        self.setObjectName("Find Toolbar")
        self._create_toolbar(main_window.main_window_toolbar_actions)

    def _create_toolbar(self, actions: MainWindowActions):
        """Fills the find toolbar with QActions

        :param actions: Main window actions

        """

        self.find_editor = FindEditor(self)

        self.add_widget(self.find_editor)

        self.addAction(actions.find)
        self.addAction(actions.replace)

        self.addWidget(self.get_manager_button())


class FormatToolbar(ToolBarBase):
    """The format toolbar for Nexuzy Sheet"""

    def __init__(self, main_window: QMainWindow):
        """
        :param main_window: Application main window

        """

        super().__init__("Format Toolbar", main_window)

        self.main_window = main_window
        self.setObjectName("Format Toolbar")
        self._create_toolbar(main_window.main_window_toolbar_actions)

    def _create_toolbar(self, actions: MainWindowActions):
        """Fills the format toolbar with QActions

        :param actions: Main window actions

        """

        menubar = self.main_window.menuBar()

        self.add_widget(self.main_window.widgets.font_combo)
        self.add_widget(self.main_window.widgets.font_size_combo)

        self.addAction(actions.bold)
        self.addAction(actions.italics)
        self.addAction(actions.underline)
        self.addAction(actions.strikethrough)

        self.addSeparator()

        self.add_widget(self.main_window.widgets.renderer_button)

        self.addSeparator()

        self.addAction(actions.freeze_cell)
        self.addAction(actions.lock_cell)
        self.addAction(actions.button_cell)

        self.addSeparator()

        self.addAction(actions.merge_cells)

        self.addSeparator()

        self.add_widget(self.main_window.widgets.rotate_button)
        self.add_widget(self.main_window.widgets.justify_button)
        self.add_widget(self.main_window.widgets.align_button)

        self.addSeparator()

        self.border_menu_button = QToolButton(self)
        self.border_menu_button.setText("Borders")
        self.border_menu_button.label = "Borders"
        border_submenu = menubar.format_menu.border_submenu
        self.border_menu_button.setMenu(border_submenu)
        self.border_menu_button.setIcon(Icon.border_menu)
        self.add_widget(self.border_menu_button)
        self.border_menu_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)

        self.line_width_button = QToolButton(self)
        self.line_width_button.setText("Border Width")
        self.line_width_button.label = "Border Width"
        line_width_submenu = menubar.format_menu.line_width_submenu
        self.line_width_button.setMenu(line_width_submenu)
        self.line_width_button.setIcon(Icon.format_borders)
        self.add_widget(self.line_width_button)
        self.line_width_button.setPopupMode(
            QToolButton.ToolButtonPopupMode.InstantPopup)

        self.addSeparator()

        text_color_button = self.main_window.widgets.text_color_button
        text_color_button.set_max_size(self.iconSize())
        self.add_widget(text_color_button)

        line_color_button = self.main_window.widgets.line_color_button
        line_color_button.set_max_size(self.iconSize())
        self.add_widget(line_color_button)

        background_color_button = \
            self.main_window.widgets.background_color_button
        background_color_button.set_max_size(self.iconSize())
        self.add_widget(background_color_button)

        self.addSeparator()

        self.addAction(actions.copy_format)
        self.addAction(actions.paste_format)

        self.addSeparator()

        self.addWidget(self.get_manager_button())


class ChartTemplatesToolBar(ToolBarBase):
    """Toolbar for chart dialog for inserting template chart code"""

    tooltip_tpl = "Package {} required but not installed"

    def __init__(self, parent: QWidget):
        """
        :param parent: Parent widget, e.g. chart dialog window

        """

        super().__init__("Chart templates toolbar", parent)

        self.setObjectName("Chart templates toolbar")
        self._create_toolbar(parent.actions)

    def _create_toolbar(self, actions: ChartDialogActions):
        """Fills the chart dialog toolbar with QActions

        :param actions: Chart dialog actions

        """

        self.addAction(actions.chart_pie_1_1)
        self.addAction(actions.chart_ring_1_1)
        self.addAction(actions.chart_line_1_1)
        self.addAction(actions.chart_polar_1_1)
        self.addAction(actions.chart_area_1_1)
        self.addAction(actions.chart_column_1_1)
        self.addAction(actions.chart_column_1_2)
        self.addAction(actions.chart_bar_1_3)
        self.addAction(actions.chart_scatter_1_1)
        self.addAction(actions.chart_bubble_1_1)
        self.addAction(actions.chart_boxplot_2_2)
        self.addAction(actions.chart_histogram_1_1)
        self.addAction(actions.chart_histogram_1_4)
        self.addAction(actions.chart_scatterhist_1_1)
        self.addAction(actions.chart_matrix_1_1)
        self.addAction(actions.chart_contour_1_2)
        self.addAction(actions.chart_surface_2_1)

        self.addWidget(self.get_manager_button())


class RChartTemplatesToolBar(ToolBarBase):
    """Toolbar for chart dialog for inserting R template chart code

    Requires rpy2 with ggplot, lattice and graphics packages

    """

    tooltip_tpl = "R Package {} required but not installed"

    def __init__(self, parent: QWidget):
        """
        :param parent: Parent widget, e.g. chart dialog window

        """

        super().__init__("Chart templates toolbar", parent)

        if rpy2 is None:
            self.close()

        self.setObjectName("R Chart templates toolbar")
        self._create_toolbar(parent.actions)

    @staticmethod
    def is_r_package_installed(package_name):
        """True if the R package is installed

        :param package_name: Name of R package to checked

        """

        if rpy2 is None:
            return False

        try:
            importr(package_name)
        except RuntimeError:
            return False
        except PackageNotInstalledError:
            return False
        return True

    def _create_toolbar(self, actions: ChartDialogActions):
        """Fills the chart dialog toolbar with QActions

        :param actions: Chart dialog actions

        """

        self.addAction(actions.chart_r_graphics_barplot_1_1)
        self.addAction(actions.chart_r_ggplot2_geom_boxplot_1_2)
        self.addAction(actions.chart_r_ggplot2_geom_point_1_1)
        self.addAction(actions.chart_r_lattice_xyplot_1_1)
        self.addAction(actions.chart_r_ggplot2_geom_density2d_1_2)
        self.addAction(actions.chart_r_lattice_wireframe_2_1)
        self.addAction(actions.chart_plotnine_geom_bar_1_1)

        if not self.is_r_package_installed("graphics"):
            tooltip = self.tooltip_tpl.format("graphics")
            actions.chart_r_graphics_barplot_1_1.setEnabled(False)
            actions.chart_r_graphics_barplot_1_1.setToolTip(tooltip)

        if not self.is_r_package_installed("lattice"):
            tooltip = self.tooltip_tpl.format("lattice")
            actions.chart_r_lattice_xyplot_1_1.setEnabled(False)
            actions.chart_r_lattice_xyplot_1_1.setToolTip(tooltip)
            actions.chart_r_lattice_wireframe_2_1.setEnabled(False)
            actions.chart_r_lattice_wireframe_2_1.setToolTip(tooltip)

        if not self.is_r_package_installed("ggplot2"):
            tooltip = self.tooltip_tpl.format("ggplot2")
            actions.chart_r_ggplot2_geom_boxplot_1_2.setEnabled(False)
            actions.chart_r_ggplot2_geom_boxplot_1_2.setToolTip(tooltip)
            actions.chart_r_ggplot2_geom_point_1_1.setEnabled(False)
            actions.chart_r_ggplot2_geom_point_1_1.setToolTip(tooltip)
            actions.chart_r_ggplot2_geom_density2d_1_2.setEnabled(False)
            actions.chart_r_ggplot2_geom_density2d_1_2.setToolTip(tooltip)

        if plotnine is None:
            tooltip = self.tooltip_tpl.format("plotnine")
            actions.chart_plotnine_geom_bar_1_1.setEnabled(False)
            actions.chart_plotnine_geom_bar_1_1.setToolTip(tooltip)

        self.addWidget(self.get_manager_button())

