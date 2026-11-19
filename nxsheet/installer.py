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

* :class:`Module`
* :class:`DependenciesDialog`
* :class:`InstallPackageDialog`

"""


try:
    from dataclasses import dataclass
except ImportError:
    # Python 3.6 compatibility
    from nxsheet.lib.dataclasses import dataclass
import os
import sys

from importlib.metadata import PackageNotFoundError, distributions, version as version__
try:
    from importlib.metadata import packages_distributions
except ImportError:
    packages_distributions = None

from PyQt6.QtCore import QProcess, QSize
from PyQt6.QtGui import QFont, QTextCursor
from PyQt6.QtWidgets import (
        QDialog, QButtonGroup, QVBoxLayout, QHBoxLayout, QTreeWidgetItem,
        QToolButton, QGroupBox, QTreeWidget, QCheckBox, QLineEdit,
        QPlainTextEdit, QWidget, QPushButton, QAbstractScrollArea)

try:
    from packaging import version
except ImportError:
    # We fall back to local library to remove the dependency
    try:
        from nxsheet.lib.packaging import version
    except ImportError:
        from lib.packaging import version
try:
    from nxsheet.lib.attrdict import AttrDict
except ImportError:
    from lib.attrdict import AttrDict


#: Distribution names whose import name differs from the distribution name.
#: Without this map ``python-dateutil`` is looked up as ``python_dateutil``
#: and reported as not installed even though it is available.
MODULE_NAMES = {
    "python-dateutil": "dateutil",
    "py-moneyed": "moneyed",
    "pyenchant": "enchant",
    "plotnine": "plotnine",
    "pycel": "pycel",
    "rpy2": "rpy2",
    "scikit-learn": "sklearn",
    "beautifulsoup4": "bs4",
}

MODULE_VERSION_ATTRS = {
    "PyQt6": "PYQT_VERSION_STR",
    "numpy": "__version__",
    "markdown2": "__version__",
    "matplotlib": "__version__",
    "openpyxl": "__version__",
    "plotnine": "__version__",
    "pycel": "__version__",
    "python-dateutil": "__version__",
    "pyenchant": "__version__",
    "py-moneyed": "__version__",
    "rpy2": "__version__",
}


@dataclass
class Module:
    """Module checker"""

    name: str
    description: str
    required_version: str  # The minimum version number that is required

    @property
    def version(self) -> version:
        """Return the installed package version, or None if absent."""

        try:
            return version.parse(version__(self.name))
        except PackageNotFoundError:
            module_version = self._module_version()
            if module_version is not None:
                return module_version
            bundled_version = self._bundled_version()
            if bundled_version is not None:
                return bundled_version
            return self._frozen_module_version()

    def _module_version(self) -> version:
        """Returns version from the imported module, None if unavailable"""

        distribution = self.name.split("[")[0]
        candidates = []
        if distribution in MODULE_NAMES:
            candidates.append(MODULE_NAMES[distribution])
        candidates.append(distribution.replace("-", "_"))
        candidates.append(distribution.lower().replace("-", "_"))

        module = None
        module_name = distribution.replace("-", "_")
        for candidate in candidates:
            try:
                module = __import__(candidate)
            except Exception:
                continue
            module_name = candidate
            break

        if module is None:
            return

        module_version = getattr(
            module, MODULE_VERSION_ATTRS.get(self.name, "__version__"), None)

        if module_version is None and module_name == "PyQt6":
            try:
                from PyQt6.QtCore import PYQT_VERSION_STR
                module_version = PYQT_VERSION_STR
            except ImportError:
                return

        if module_version is None:
            return self._distribution_version_from_import_name(module_name)

        if module_version is None and module_name == "PyQt6":
            try:
                from PyQt6.QtCore import PYQT_VERSION_STR
                module_version = PYQT_VERSION_STR
            except ImportError:
                return

        try:
            return version.parse(str(module_version))
        except ValueError:
            return self._distribution_version_from_import_name(module_name)

    def _distribution_version_from_import_name(self, module_name: str):
        """Resolve a distribution version through its top-level import name."""
        if packages_distributions is None:
            return
        try:
            names = packages_distributions().get(module_name, [])
            for name in names:
                try:
                    return version.parse(version__(name))
                except PackageNotFoundError:
                    continue
        except (ImportError, OSError, ValueError):
            return

    def _bundled_version(self) -> version:
        """Find version information retained in a frozen application."""
        if not getattr(sys, "frozen", False):
            return

        try:
            for distribution in distributions():
                if distribution.metadata.get("Name", "").lower() == self.name.lower():
                    return version.parse(distribution.version)
        except Exception:
            return

    def _frozen_module_version(self) -> version:
        """Resolve package versions from PyInstaller's bundled imports."""
        if not getattr(sys, "frozen", False):
            return
        module_name = MODULE_NAMES.get(self.name, self.name.replace("-", "_"))
        try:
            module = __import__(module_name)
        except Exception:
            return
        value = getattr(module, MODULE_VERSION_ATTRS.get(self.name, "__version__"), None)
        if value is None:
            return self._distribution_version_from_import_name(module_name)
        try:
            return version.parse(str(value))
        except ValueError:
            return

    def is_installed(self) -> bool:
        """True if the module is installed"""

        __version = self.version

        return bool(__version) if __version is not None else None

# Required dependencies
# ---------------------

# Required dependencies are checked by the cli


REQUIRED_DEPENDENCIES = [
    Module(name="markdown2",
           description="Python implementation of Markdown.",
           required_version=version.parse("2.3")),
    Module(name="numpy",
           description="Fundamental package for scientific computing.",
           required_version=version.parse("1.1")),
    Module(name="PyQt6",
           description="Python bindings for the Qt application framework.",
           required_version=version.parse("6.5")),
]

# Optional dependencies
# ---------------------


OPTIONAL_DEPENDENCIES = [
    Module(name="matplotlib",
           description="Create visualizations in Python.",
           required_version=version.parse("3.4")),
    Module(name="openpyxl",
           description="Read Excel 2010 xlsx files.",
           required_version=version.parse("3.0.7")),
    Module(name="plotnine",
           description="Grammar of graphics for simpler R ggplot2 charts.",
           required_version=version.parse("0.8")),
    Module(name="pycel",
           description="Translate an Excel spreadsheet into executable python "
                       "code.",
           required_version=version.parse("1.0b30")),
    Module(name="python-dateutil",
           description="Parse date strings.",
           required_version=version.parse("2.7.0")),
    Module(name="pyenchant",
           description="Bindings for the Enchant spellchecking library.",
           required_version=version.parse("1.1")),
    Module(name="py-moneyed",
           description="Money class for csv import and usage in cells.",
           required_version=version.parse("2.0")),
    Module(name="rpy2",
           description="Interface to R, required for R charts.",
           required_version=version.parse("3.4")),
]

DEPENDENCIES = REQUIRED_DEPENDENCIES + OPTIONAL_DEPENDENCIES

PIP_MODULE = Module(name="pip", description="pip installer",
                    required_version=version.parse("17.0"))

# Not yet implemented modules
#    Module(name="xlrd",
#           description="Load Excel files",
#           required_version="0.9.2"),
#    Module(name="xlwt",
#           description="Save Excel files",
#           required_version="0.9.2"),


class DependenciesDialog(QDialog):
    """Dependencies dialog for python dependencies"""

    column = AttrDict(zip(("button", "status", "name", "version",
                           "required_version", "description"), range(6)))
    column_headers = ("", "Status", "Package", "Version", "Required",
                      "Description")

    def __init__(self, parent: QWidget = None):
        """
        :param parent: Parent widget

        """

        super().__init__(parent)

        self.setWindowTitle("Installer")

        # Button group for install buttons
        self.buttGroup = QButtonGroup()
        self.buttGroup.buttonClicked.connect(self.on_butt_install)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.mainLayout)

        self.tree = QTreeWidget()
        self.tree.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.mainLayout.addWidget(self.tree, 4)

        self.tree.setHeaderLabels(self.column_headers)
        self.tree.setRootIsDecorated(False)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.NoSelection)

        self.update_load()

    def update_load(self):

        self.tree.clear()

        for module in DEPENDENCIES:
            item = QTreeWidgetItem()
            if module in REQUIRED_DEPENDENCIES:
                item.setText(self.column.button, "Required")
            else:
                item.setText(self.column.button, "Optional")
            item.setText(self.column.name, module.name)
            version = module.version if module.version else "Not installed"
            item.setText(self.column.version, str(version))
            item.setText(self.column.required_version,
                         str(module.required_version))
            item.setText(self.column.description, module.description)
            self.tree.addTopLevelItem(item)

            if module.is_installed():
                status = "Installed"
                bold = False
            else:
                status = "Not installed"
                bold = True
                butt = QToolButton()
                butt.setText("Install")
                butt.setEnabled(PIP_MODULE.is_installed())
                self.tree.setItemWidget(item, self.column.button, butt)
                self.buttGroup.addButton(butt, DEPENDENCIES.index(module))

            item.setText(self.column.status, status)
            if bold:
                item.setFont(self.column.status, QFont("", -1, QFont.Weight.Bold))

        for col in range(self.tree.columnCount()):
            self.tree.resizeColumnToContents(col)

    def on_butt_install(self, butt: QPushButton):
        """One of install buttons pressed

        :param butt: The pressed button

        """

        butt.setDisabled(True)
        idx = self.buttGroup.id(butt)

        dial = InstallPackageDialog(self, module=DEPENDENCIES[idx])
        dial.exec()
        self.update_load()


class InstallPackageDialog(QDialog):
    """Shows a dialog to execute command"""

    line_str = "-" * 56

    def __init__(self, parent=None, module=None):
        """
        :param parent: Parent widget
        :param module: Module to be installed

        """

        super().__init__(parent)

        self.module = module

        self.setWindowTitle("Install Package")
        self.setMinimumWidth(600)

        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.on_read_standard)
        self.process.readyReadStandardError.connect(self.on_read_error)
        self.process.finished.connect(self.on_finished)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(self.mainLayout)

        self.groupBox = QGroupBox()
        self.groupBox.setTitle("Shell Command")
        self.groupBoxLayout = QHBoxLayout()
        self.groupBox.setLayout(self.groupBoxLayout)
        self.mainLayout.addWidget(self.groupBox)

        self.buttSudo = QCheckBox()
        self.buttSudo.setText("sudo")
        self.groupBoxLayout.addWidget(self.buttSudo, 0)
        self.buttSudo.toggled.connect(self.update_cmd_line)
        self.buttSudo.setVisible(os.name != "nt")

        self.txtCommand = QLineEdit()
        self.groupBoxLayout.addWidget(self.txtCommand, 10)

        self.buttExecute = QPushButton()
        self.buttExecute.setText("Execute")
        self.groupBoxLayout.addWidget(self.buttExecute, 0)
        self.buttExecute.clicked.connect(self.on_butt_execute)

        self.txtStdOut = QPlainTextEdit()
        self.mainLayout.addWidget(self.txtStdOut)

        self.txtStdErr = QPlainTextEdit()
        self.mainLayout.addWidget(self.txtStdErr)

        self.update_cmd_line()

    def update_cmd_line(self, *unused):
        """Update the commend line considering sudo button state"""

        cmd = ""
        if self.buttSudo.isChecked():
            cmd += "pkexec  "

        cmd += "pip3 install {modulename}".format(modulename=self.module.name)

        self.txtCommand.setText(cmd)

    def on_butt_execute(self):
        """Execute button event handler"""

        self.buttSudo.setDisabled(True)
        self.buttExecute.setDisabled(True)

        self.txtStdOut.setPlainText("")
        self.txtStdErr.setPlainText("")
        self.process.start(self.txtCommand.text())

    def on_read_standard(self):
        """Stdout read event handler"""

        msg_tpl = "{}\n{}\n{}"
        msg = msg_tpl.format(self.txtStdOut.toPlainText(),
                             self.line_str,
                             self.process.readAllStandardOutput())

        self.txtStdOut.setPlainText(msg)
        self.txtStdOut.moveCursor(QTextCursor.End)

    def on_read_error(self):
        """Stderr read event handler"""

        msg_tpl = "{}\n{}\n{}"
        msg = msg_tpl.format(self.txtStdErr.toPlainText(),
                             self.line_str,
                             self.process.readAllStandardError())

        self.txtStdErr.setPlainText(msg)
        self.txtStdErr.moveCursor(QTextCursor.End)

    def on_finished(self):
        """Execution finished event handler"""

        self.buttSudo.setDisabled(False)
        self.buttExecute.setDisabled(False)

