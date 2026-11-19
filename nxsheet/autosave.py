# -*- coding: utf-8 -*-

# Copyright (c) 2026 Nexuzy Lab
# Nexuzy Sheet
#
# Developed by Nexuzy Lab
# Website: https://nexuzy.in
#
# Licensed under the MIT License. See the LICENSE file in the project
# root for the full license text.
# --------------------------------------------------------------------

"""

**Provides**

 * :data:`APP_DATA_DIR`
 * :func:`write_workbook`
 * :class:`AutoSaveManager`
 * :class:`VersionHistoryDialog`

Nexuzy Sheet keeps two safety nets next to the normal save action:

* **Auto save** writes a recovery copy of the current workbook into
  ``~/.nexuzy_sheet/autosave`` every :attr:`settings.Settings.autosave_interval`
  seconds while the document has unsaved changes.
* **Automatic backup** copies the workbook into
  ``~/.nexuzy_sheet/backups/<workbook name>`` after every successful save and
  keeps :attr:`settings.Settings.max_backups` versions.

:class:`VersionHistoryDialog` lists both kinds of copies and restores them.

"""

import bz2
import shutil
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QAbstractItemView, QDialog, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout)

try:
    from nxsheet.interfaces.pys import PysWriter
except ImportError:
    from interfaces.pys import PysWriter


#: Directory that holds all Nexuzy Sheet user data
APP_DATA_DIR = Path.home() / ".nexuzy_sheet"

#: Suffix of auto save recovery files
RECOVERY_SUFFIX = ".autosave.nix"

#: Suffixes that are treated as Nexuzy Sheet workbooks
WORKBOOK_SUFFIXES = (".nix", ".nxl", ".nxs")


def write_workbook(code_array, filepath: Path) -> Path:
    """Writes a compressed Nexuzy Sheet workbook without touching the UI

    The workbook is written to a temporary file first so that an interrupted
    auto save never leaves a truncated file behind.

    :param code_array: The :class:`model.model.CodeArray` to be saved
    :param filepath: Target path of the ``.nix`` file
    :return: The written path

    """

    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    content = "".join(PysWriter(code_array)).encode("utf-8")

    temporary = filepath.with_name(filepath.name + ".part")
    with bz2.open(temporary, "wb") as outfile:
        outfile.write(content)
    temporary.replace(filepath)

    return filepath


def _human_size(size: int) -> str:
    """Returns a human readable file size

    :param size: File size in bytes

    """

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


class AutoSaveManager:
    """Triggers auto save recovery copies and automatic backups"""

    def __init__(self, main_window):
        """
        :param main_window: Nexuzy Sheet main window

        """

        self.main_window = main_window
        self.settings = main_window.settings
        self.last_autosave = None
        self.last_error = None

        self.timer = QTimer(main_window)
        self.timer.timeout.connect(self.run)

    # Folders

    @property
    def autosave_dir(self) -> Path:
        """Directory for recovery copies"""

        return Path(getattr(self.settings, "autosave_dir",
                            APP_DATA_DIR / "autosave"))

    @property
    def backup_root(self) -> Path:
        """Root directory of the automatic backups"""

        return Path(getattr(self.settings, "backup_dir",
                            APP_DATA_DIR / "backups"))

    def backup_dir_for(self, filepath: Path) -> Path:
        """Returns the backup folder of a workbook

        :param filepath: Path of the workbook

        """

        return self.backup_root / Path(filepath).stem

    # Timer

    def start(self) -> None:
        """Starts the auto save timer if auto save is enabled"""

        self.restart()

    def stop(self) -> None:
        """Stops the auto save timer"""

        self.timer.stop()

    def restart(self) -> None:
        """Applies the current interval and enabled state to the timer"""

        interval = max(30, int(getattr(self.settings, "autosave_interval",
                                       120)))
        if getattr(self.settings, "autosave_enabled", True):
            self.timer.start(interval * 1000)
        else:
            self.timer.stop()

    # Workbook helpers

    def workbook_path(self):
        """Returns the saved workbook path or None for an unsaved document"""

        candidate = Path(str(self.settings.last_file_output_path))
        if candidate.suffix.lower() in WORKBOOK_SUFFIXES:
            return candidate
        return None

    def recovery_path(self) -> Path:
        """Returns the recovery copy path of the current workbook"""

        workbook = self.workbook_path()
        stem = workbook.stem if workbook is not None else "untitled"
        return self.autosave_dir / f"{stem}{RECOVERY_SUFFIX}"

    # Actions

    def run(self) -> None:
        """Timer handler that writes the recovery copy"""

        if not getattr(self.settings, "autosave_enabled", True):
            return
        if not getattr(self.settings, "changed_since_save", False):
            return

        try:
            path = write_workbook(
                self.main_window.grid.model.code_array, self.recovery_path())
        except Exception as error:  # Keep the app alive on any IO error
            self.last_error = error
            self.main_window.statusBar().showMessage(
                f"Auto save failed: {error}")
            return

        self.last_autosave = datetime.now()
        self.last_error = None
        self.main_window.statusBar().showMessage(
            f"Auto saved recovery copy: {path}")

    def on_saved(self, filepath: Path) -> None:
        """Called after a successful manual save

        Clears the recovery copy and creates the automatic backup.

        :param filepath: Path of the saved workbook

        """

        filepath = Path(filepath)

        try:
            recovery = self.autosave_dir / \
                f"{filepath.stem}{RECOVERY_SUFFIX}"
            if recovery.is_file() and \
                    recovery.resolve() != filepath.resolve():
                recovery.unlink()
        except OSError:
            pass

        if not getattr(self.settings, "backup_enabled", True):
            return
        self.create_backup(filepath)

    def create_backup(self, filepath: Path):
        """Creates a timestamped backup of a saved workbook

        :param filepath: Path of the workbook that was just saved
        :return: Path of the backup or None

        """

        filepath = Path(filepath)
        if not filepath.is_file():
            return None

        try:
            folder = self.backup_dir_for(filepath)
            folder.mkdir(parents=True, exist_ok=True)
            now = datetime.now()
            stamp = f"{now:%Y%m%d-%H%M%S}-{now.microsecond // 1000:03d}"
            suffix = filepath.suffix or ".nix"
            target = folder / f"{filepath.stem}-{stamp}{suffix}"
            shutil.copy2(filepath, target)
        except OSError as error:
            self.last_error = error
            return None

        self.prune_backups(folder)
        return target

    def prune_backups(self, folder: Path) -> None:
        """Removes the oldest backups of a workbook folder

        :param folder: Backup folder of one workbook

        """

        limit = max(1, int(getattr(self.settings, "max_backups", 20)))
        try:
            backups = sorted(folder.glob("*"), key=lambda p: p.stat().st_mtime,
                             reverse=True)
        except OSError:
            return

        for old in backups[limit:]:
            try:
                old.unlink()
            except OSError:
                pass

    def backup_on_close(self) -> None:
        """Writes a final recovery copy when the application is closed"""

        if getattr(self.settings, "changed_since_save", False):
            self.run()

    # Version history

    def history_entries(self):
        """Returns all recovery copies and backups, newest first

        :return: List of ``(path, kind, timestamp, size)`` tuples

        """

        entries = []
        folders = [(self.autosave_dir, "Recovery")]
        if self.backup_root.is_dir():
            for folder in self.backup_root.iterdir():
                if folder.is_dir():
                    folders.append((folder, "Backup"))

        for folder, kind in folders:
            if not folder.is_dir():
                continue
            for path in folder.glob("*"):
                if not path.is_file() or path.name.endswith(".part"):
                    continue
                if path.suffix.lower() not in WORKBOOK_SUFFIXES:
                    continue
                try:
                    stat = path.stat()
                except OSError:
                    continue
                entries.append((path, kind,
                                datetime.fromtimestamp(stat.st_mtime),
                                stat.st_size))

        entries.sort(key=lambda entry: entry[2], reverse=True)
        return entries


class VersionHistoryDialog(QDialog):
    """Lists auto save recovery copies and automatic backups"""

    window_title = "Version history"

    def __init__(self, main_window):
        """
        :param main_window: Nexuzy Sheet main window

        """

        super().__init__(main_window)

        self.main_window = main_window
        self.autosave = main_window.autosave

        self.setWindowTitle(self.window_title)
        self.setMinimumSize(680, 420)

        info = QLabel("Auto saved recovery copies and automatic backups of "
                      "Nexuzy Sheet workbooks. Select a version and restore "
                      "it.", self)

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Workbook", "Saved", "Size", "Kind"])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.itemDoubleClicked.connect(self.on_restore)

        self.restore_button = QPushButton("Restore", self)
        self.restore_button.clicked.connect(self.on_restore)
        delete_button = QPushButton("Delete", self)
        delete_button.clicked.connect(self.on_delete)
        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.reject)
        refresh_button = QPushButton("Refresh", self)
        refresh_button.clicked.connect(self.update_)

        buttons = QHBoxLayout()
        buttons.addWidget(refresh_button)
        buttons.addStretch(1)
        buttons.addWidget(self.restore_button)
        buttons.addWidget(delete_button)
        buttons.addWidget(close_button)

        layout = QVBoxLayout(self)
        layout.addWidget(info)
        layout.addWidget(self.tree, 1)
        layout.addLayout(buttons)

        self.update_()

    def update_(self) -> None:
        """Fills the tree with the available versions"""

        self.tree.clear()

        for path, kind, timestamp, size in self.autosave.history_entries():
            item = QTreeWidgetItem([
                path.name,
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                _human_size(size),
                kind,
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, str(path))
            item.setToolTip(0, str(path))
            self.tree.addTopLevelItem(item)

        self.tree.resizeColumnToContents(0)
        self.restore_button.setEnabled(
            self.tree.topLevelItemCount() > 0)

    def selected_path(self):
        """Returns the path of the selected version or None"""

        item = self.tree.currentItem()
        if item is None:
            return None
        return Path(item.data(0, Qt.ItemDataRole.UserRole))

    def on_restore(self, *args) -> None:
        """Opens the selected version in the grid"""

        path = self.selected_path()
        if path is None:
            QMessageBox.information(self, "Version history",
                                    "Select a version first.")
            return

        if not path.is_file():
            QMessageBox.warning(self, "Version history",
                                f"{path} does not exist any more.")
            self.update_()
            return

        answer = QMessageBox.question(
            self, "Restore version",
            f"Open {path.name} from\n{path.parent}\n\n"
            "Unsaved changes in the current workbook are discarded. "
            "Continue?")
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.accept()
        self.main_window.workflows.filepath_open(path)
        self.main_window.workflows.update_main_window_title()

    def on_delete(self) -> None:
        """Deletes the selected version after confirmation"""

        path = self.selected_path()
        if path is None:
            QMessageBox.information(self, "Version history",
                                    "Select a version first.")
            return

        answer = QMessageBox.question(
            self, "Delete version", f"Delete {path.name} permanently?")
        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            path.unlink()
        except OSError as error:
            QMessageBox.critical(self, "Delete version", str(error))
        self.update_()
