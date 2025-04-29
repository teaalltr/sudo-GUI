"""
Tab package – re-export public tab widgets used by main_window.SudoGUI.
"""
from .list_tab import ListTab
from .defaults_tab import DefaultsTab
from .alias_tab import AliasTab
from .plugins_tab import PluginsTab

__all__: list[str] = [
    "ListTab",
    "DefaultsTab",
    "AliasTab",
    "PluginsTab",
]
