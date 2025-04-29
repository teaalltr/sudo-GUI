"""
main_window.py – top-level GUI window for the sudoers-safe-edit application.

Holds one public symbol:

    SudoGUI  – a QMainWindow that wires together the toolbar, the editable
               tabs, validation logic, visudo save routine and help dialog.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QFontDatabase
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from .constants import SUDOERS_PATH
from .parser import parse_sudoers, get_plugins
from .tabs.defaults_tab import DefaultsTab
from .tabs.alias_tab import AliasTab
from .tabs.plugins_tab import PluginsTab


class SudoGUI(QMainWindow):
    """Primary application window."""

    # ------------------------------------------------------------------ #
    #  Construction
    # ------------------------------------------------------------------ #
    def __init__(self) -> None:                             # noqa: D401
        super().__init__()

        self.setWindowTitle("sudoers editor – safe mode")
        self.resize(880, 640)
        self.setUnifiedTitleAndToolBarOnMac(True)

        # === Toolbar ====================================================
        toolbar = QToolBar("Main", self)
        self.addToolBar(toolbar)

        open_btn = QPushButton("Open…", self)
        open_btn.clicked.connect(lambda _=False: self.open_sudoers())
        toolbar.addWidget(open_btn)

        self.save_btn = QPushButton("Save", self)
        self.save_btn.clicked.connect(self.save_sudoers)
        self.save_btn.setEnabled(False)
        toolbar.addWidget(self.save_btn)

        # Auto-load preference
        self.settings = QSettings("ExampleOrg", "sudoers-safe-edit")
        autoload = self.settings.value("autoload", True, bool)

        self.autoload_act = QAction(
            "Auto-load /etc/sudoers on start", self,
            checkable=True, checked=autoload
        )
        self.autoload_act.toggled.connect(self._save_autoload_pref)
        toolbar.addAction(self.autoload_act)
        self.menuBar().addMenu("&File").addAction(self.autoload_act)

        # Edit mode toggle
        self.edit_toggle = QPushButton("Enable editing", self, checkable=True)
        self.edit_toggle.toggled.connect(self.set_editable)
        toolbar.addWidget(self.edit_toggle)

        # === Central tab widget =========================================
        self.tabs = QTabWidget(self)

        self.defaults_tab = DefaultsTab()
        self.alias_tab = AliasTab()
        self.plugins_tab = PluginsTab()

        # Raw view
        self.raw_tab = QWidget(self)
        self.raw_label = QLabel(self.raw_tab)
        self.raw_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        mono = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        self.raw_label.setFont(mono)
        self.raw_tab.setLayout(QVBoxLayout())
        self.raw_tab.layout().addWidget(self.raw_label)

        self.tabs.addTab(self.defaults_tab, "Defaults")
        self.tabs.addTab(self.alias_tab, "Aliases")
        self.tabs.addTab(self.plugins_tab, "Plugins")
        self.tabs.addTab(self.raw_tab, "Raw view")

        self.setCentralWidget(self.tabs)

        # === Help =======================================================
        help_act = QAction("&How to use…", self)
        help_act.triggered.connect(self.show_help)
        self.menuBar().addMenu("&Help").addAction(help_act)

        # === State ======================================================
        self.current_file: str | None = None
        self.original_text: str = ""

        self.defaults_tab.changed.connect(self._update_validation)
        self.alias_tab.changed.connect(self._update_validation)

        # Maybe auto-open on launch
        if autoload:
            self.open_sudoers(SUDOERS_PATH)

    # ------------------------------------------------------------------ #
    #  UI helpers
    # ------------------------------------------------------------------ #
    def set_editable(self, enable: bool) -> None:
        """Toggle cell editability in the two editable tabs."""
        trigger = (QAbstractItemView.EditTrigger.DoubleClicked
                   if enable else QAbstractItemView.EditTrigger.NoEditTriggers)
        for tab in (self.defaults_tab, self.alias_tab):
            tab.table.setEditTriggers(trigger)

        self.edit_toggle.setText("Disable editing" if enable else "Enable editing")
        self._update_validation()

    def _update_validation(self) -> None:
        """Enable Save only when edit mode is on *and* both tabs validate."""
        valid = (self.edit_toggle.isChecked() and
                 self.defaults_tab.validate() and
                 self.alias_tab.validate())
        self.save_btn.setEnabled(valid)

    def _save_autoload_pref(self, state: bool) -> None:
        self.settings.setValue("autoload", state)

    # ------------------------------------------------------------------ #
    #  File I/O
    # ------------------------------------------------------------------ #
    def open_sudoers(self, preset_path: str | None = None) -> None:
        """Load a sudoers file and populate all tabs."""
        path = preset_path
        if path is None:
            path, _ = QFileDialog.getOpenFileName(
                self, "Open sudoers", SUDOERS_PATH
            )
            if not path:
                return

        try:
            text = Path(path).read_text()
        except Exception as exc:                              # noqa: BLE001
            QMessageBox.critical(self, "Error", str(exc))
            return

        self.current_file, self.original_text = path, text
        self.populate_tabs(text)
        self.edit_toggle.setChecked(False)    # start read-only

    def populate_tabs(self, text: str) -> None:
        defaults, aliases, _rules = parse_sudoers(text)

        self.defaults_tab.populate(
            [d.split("=", 1) if "=" in d else (d, "") for d in defaults]
        )
        self.alias_tab.populate(
            [(f"{t}_Alias {n}", v) for t, n, v in aliases]
        )
        self.plugins_tab.populate(get_plugins())

        self.raw_label.setText(f"<pre>{text}</pre>")

    def save_sudoers(self) -> None:
        """Collect edits, run visudo checks, backup & save."""
        if not self.current_file:
            QMessageBox.information(self, "Nothing to save", "Open a file first.")
            return
        if not self.edit_toggle.isChecked():
            QMessageBox.information(self, "Read-only", "Enable editing first.")
            return

        # --- collect edited Defaults ------------------------------------
        new_defaults: list[str] = []
        tab = self.defaults_tab.table
        for row in range(tab.rowCount()):
            key = tab.item(row, 0).text().strip()
            val = tab.item(row, 1).text().strip()
            new_defaults.append(
                f"Defaults {key}={val}" if val else f"Defaults {key}"
            )

        # --- collect edited Aliases -------------------------------------
        new_aliases: list[str] = []
        tab = self.alias_tab.table
        for row in range(tab.rowCount()):
            alias_name = tab.item(row, 0).text().split()[-1]
            alias_val = tab.item(row, 1).text().strip()
            new_aliases.append(f"{alias_name} = {alias_val}")

        # --- merge with untouched lines ---------------------------------
        untouched_lines = [
            ln for ln in self.original_text.splitlines()
            if not (ln.strip().startswith("Defaults") or "_Alias" in ln)
        ]
        merged = "\n".join(new_defaults + new_aliases + untouched_lines) + "\n"

        # --- visudo sanity check ----------------------------------------
        tmp_path = Path("/tmp/sudoers.qtmp")
        tmp_path.write_text(merged)

        if subprocess.call(["sudo", "visudo", "-c", "-f", str(tmp_path)]) != 0:
            QMessageBox.critical(self, "Syntax error", "visudo reported errors.")
            tmp_path.unlink(missing_ok=True)
            return

        # --- backup original --------------------------------------------
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = f"{self.current_file}.bak-{timestamp}"
        try:
            shutil.copy2(self.current_file, backup)
        except Exception as exc:                              # noqa: BLE001
            QMessageBox.warning(
                self, "Backup failed",
                f"Could not create backup '{backup}': {exc}"
            )

        # --- write via visudo -------------------------------------------
        if subprocess.call(["sudo", "visudo", "-s", "-f", str(tmp_path)]) == 0:
            QMessageBox.information(
                self, "Saved",
                f"sudoers updated successfully.\nBackup: {backup}"
            )
            self.original_text = merged
            self.edit_toggle.setChecked(False)
            self.open_sudoers()          # reload to refresh raw view
        else:
            QMessageBox.critical(self, "Save failed",
                                 "visudo refused the new file.")

        tmp_path.unlink(missing_ok=True)

    # ------------------------------------------------------------------ #
    #  Help
    # ------------------------------------------------------------------ #
    def show_help(self) -> None:
        text = (
            "<h3>Quick how-to</h3>"
            "<ol>"
            "<li><b>Open</b> an existing sudoers file "
            "(the default path is pre-selected).</li>"
            "<li>Browse the tabs. <i>Plugins</i> and <i>Raw view</i> are read-only.</li>"
            "<li>Press <b>Enable editing</b> to unlock the two editable tabs.</li>"
            "<li>Yellow cells are modified; red rows have validation errors.</li>"
            "<li>When everything is valid, the <b>Save</b> button becomes active.<br>"
            "A timestamped backup is written next to the original file before saving.</li>"
            "<li>All edits go through <code>visudo</code>, "
            "so it is impossible to write an invalid file.</li>"
            "</ol>"
        )
        QMessageBox.information(self, "Help – sudoers editor", text)
