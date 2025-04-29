"""
list_tab.py
-----------
Abstract base class for every page that shows a two-column (or more) QTableWidget
plus a short descriptive label.  Handles:

* uniform help label styling
* "yellow when changed" cell tinting
* plumbing of a **changed** signal so the main window can re-validate
"""

from __future__ import annotations

from typing import List, Tuple

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)

from ..color_utils import changed_bg, error_bg


class ListTab(QWidget):
    """
    A labelled `QTableWidget`.

    Sub-classes should override:

        * populate()
        * validate_row()

    and may emit **changed** whenever edits occur.
    """

    changed = pyqtSignal()                      # emitted on any cell edit

    # ------------------------------------------------------------------ #
    # Construction
    # ------------------------------------------------------------------ #
    def __init__(self, header1: str, header2: str, help_text: str) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        # ---- top help label -------------------------------------------
        help_lbl = QLabel(help_text, self)
        fnt: QFont = help_lbl.font()
        fnt.setPointSizeF(fnt.pointSizeF() * 0.9)       # slightly smaller
        help_lbl.setFont(fnt)
        help_lbl.setWordWrap(True)
        layout.addWidget(help_lbl)

        # ---- central table --------------------------------------------
        self.table = QTableWidget(
            0, 2, self,
            editTriggers=QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setHorizontalHeaderLabels([header1, header2])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        # tool-tips on header cells
        self.table.horizontalHeaderItem(0).setToolTip(header1)
        self.table.horizontalHeaderItem(1).setToolTip(header2)

        self.table.itemChanged.connect(self._mark_changed)
        layout.addWidget(self.table)

    # ------------------------------------------------------------------ #
    # Population helper – override in concrete tabs if needed
    # ------------------------------------------------------------------ #
    def populate(self, rows: List[Tuple[str, str]]) -> None:             # noqa: D401
        self.table.blockSignals(True)
        self.table.setRowCount(0)

        for r in rows:
            row = self.table.rowCount()
            self.table.insertRow(row)
            for col, text in enumerate(r):
                itm = QTableWidgetItem(text)
                # store original value for "has changed?" comparison
                itm.setData(Qt.ItemDataRole.UserRole, text)
                itm.setFlags(itm.flags() | Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, col, itm)

        self.table.blockSignals(False)

    # ------------------------------------------------------------------ #
    # Edit tracking
    # ------------------------------------------------------------------ #
    def _mark_changed(self, item: QTableWidgetItem) -> None:
        """Tint cell background when edited, restore if reverted."""
        original = item.data(Qt.ItemDataRole.UserRole)
        if item.text() != original:
            item.setBackground(changed_bg(self.palette()))
        else:
            item.setBackground(self.palette().color(QPalette.ColorRole.Base))

        self.changed.emit()

    # ------------------------------------------------------------------ #
    # Validation
    # ------------------------------------------------------------------ #
    def validate_row(self, row: int) -> bool:                            # noqa: D401
        """Override per tab.  Should paint row red on failure."""
        return True

    def validate(self) -> bool:                                          # noqa: D401
        """Validate every row; return True iff the whole table is OK."""
        ok = True
        for r in range(self.table.rowCount()):
            if not self.validate_row(r):
                ok = False
        return ok

    # Utility for sub-classes
    # ----------------------
    def _err_bg(self):
        return error_bg(self.palette())
