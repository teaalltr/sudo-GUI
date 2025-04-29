"""
plugins_tab.py
--------------
Read-only view of compiled sudo plugins detected on the host.
"""

from __future__ import annotations
from typing import List, Tuple

from .list_tab import ListTab


class PluginsTab(ListTab):
    """Simple read-only two-column table."""

    def __init__(self) -> None:                                          # noqa: D401
        help_txt = (
            "Read-only list of compiled sudo plugins detected on this system."
        )
        super().__init__("Name", "Path", help_txt)

    # Plugins are populated by main_window; no extra validation needed.
    def validate(self) -> bool:                                          # noqa: D401
        return True
