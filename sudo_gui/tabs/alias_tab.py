"""
alias_tab.py
------------
Two-column editor for User/Runas/Host/Cmnd aliases.
"""

from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

from ..delegates.alias_type import AliasTypeDelegate
from ..color_utils import error_bg
from .list_tab import ListTab


class AliasTab(ListTab):
    """Editor for *_Alias* lines."""

    # ------------------------------------------------------------------ #
    def __init__(self) -> None:                                          # noqa: D401
        help_txt = (
            "<b>Aliases</b> are named lists used later in user specifications. "
            "Pick the type (User/Runas/Host/Cmnd) from the dropdown and edit "
            "the list."
        )
        super().__init__("Alias type + name", "Definition", help_txt)

        self.type_delegate = AliasTypeDelegate()
        self.table.setItemDelegateForColumn(0, self.type_delegate)

    # ------------------------------------------------------------------ #
    # Row validation
    # ------------------------------------------------------------------ #
    def validate_row(self, row: int) -> bool:                            # noqa: D401
        first = self.table.item(row, 0).text().strip()
        second = self.table.item(row, 1).text().strip()

        good = (
            bool(first) and
            bool(second) and
            "_" in first and              # must contain underscore ("*_Alias")
            "=" not in first              # but no '=' characters
        )

        self._paint_row(row, good)
        return good

    # helpers
    # -------
    def _paint_row(self, row: int, good: bool) -> None:
        bg = self.palette().base() if good else self._err_bg()
        for c in range(2):
            self.table.item(row, c).setBackground(bg)

    def _err_bg(self):
        # use a slightly different tint than DefaultsTab for variety
        return error_bg(self.palette())
