"""
defaults_tab.py
---------------
Three-column view of *Defaults* lines: Setting | Value | Meaning.
"""

from __future__ import annotations

from typing import Dict, Any

# QtCore gives us the Qt namespace used for roles/flags
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtWidgets import QHeaderView

from ..constants import DEFAULTS_META
from ..color_utils import error_bg
from ..delegates.value_delegate import ValueDelegate
from .list_tab import ListTab


class DefaultsTab(ListTab):
    """Guided editor for sudo Defaults."""

    # ------------------------------------------------------------------ #
    def __init__(self) -> None:
        help_txt = (
            "<b>Defaults</b> are global sudo options.  "
            "Values are edited with context-aware widgets:"
            "<ul><li><i>Yes/No</i> for booleans</li>"
            "<li>Combos for enumerations</li>"
            "<li>Spin-box for numeric time-outs</li></ul>"
            "Yellow = changed, Red = invalid."
        )
        super().__init__("Setting", "Value", help_txt)

        # add read-only Meaning column
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderItem(2, QTableWidgetItem("Meaning"))
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )

        # custom delegate for Value column
        self.value_delegate = ValueDelegate()
        self.table.setItemDelegateForColumn(1, self.value_delegate)

    # ------------------------------------------------------------------ #
    # Population override
    # ------------------------------------------------------------------ #
    def populate(self, rows):
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        for key, val in rows:
            meta: Dict[str, Any] = DEFAULTS_META.get(key, {})
            desc = meta.get("desc", "Custom / undocumented key.")

            r = self.table.rowCount()
            self.table.insertRow(r)

            for c, txt, editable in (
                (0, key, True),
                (1, val, True),
                (2, desc, False),
            ):
                itm = QTableWidgetItem(txt)
                itm.setData(Qt.ItemDataRole.UserRole, txt)

                if not editable:
                    # make Meaning column greyed & read-only
                    itm.setFlags(itm.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    itm.setForeground(
                        self.palette().color(
                            QPalette.ColorGroup.Disabled,
                            QPalette.ColorRole.Text,
                        )
                    )

                self.table.setItem(r, c, itm)

        self.table.blockSignals(False)

    # ------------------------------------------------------------------ #
    # Row validation
    # ------------------------------------------------------------------ #
    def validate_row(self, row: int) -> bool:
        key = self.table.item(row, 0).text().strip()
        val = self.table.item(row, 1).text().strip()
        meta = DEFAULTS_META.get(key, {})
        kind = meta.get("type", "text")

        ok = bool(key)                       # key must not be empty

        if kind == "bool":
            ok &= val in {"", "true", "false"}

        elif kind == "enum":
            ok &= val in set(meta["choices"])

        elif kind == "int":
            try:
                v = int(val)
                ok &= meta.get("min", -99_999) <= v <= meta.get("max", 99_999)
            except ValueError:
                ok = False

        # path/text → nothing more to check

        # colour the row
        self._paint_row(row, ok)
        return ok

    # helpers
    # -------
    def _paint_row(self, row: int, good: bool) -> None:
        pal = self.palette()
        self.table.blockSignals(True)
        for c in range(self.table.columnCount()):
            itm = self.table.item(row, c)
            if good:
                # keep any existing "changed" tint on edited cells
                continue
            itm.setBackground(error_bg(pal))
        self.table.blockSignals(False)
