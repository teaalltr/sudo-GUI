"""
AliasTypeDelegate
-----------------
Provides a fixed list of alias kinds for the first column in the
*Aliases* tab.
"""

from PyQt6.QtWidgets import QStyledItemDelegate, QComboBox


class AliasTypeDelegate(QStyledItemDelegate):
    """Dropdown for `User_Alias`, `Runas_Alias`, `Host_Alias`, `Cmnd_Alias`."""

    kinds: list[str] = ["User_Alias", "Runas_Alias",
                        "Host_Alias", "Cmnd_Alias"]

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(self.kinds)
        combo.setEditable(False)
        return combo

    def setEditorData(self, editor, index):
        editor.setCurrentText(index.data().split()[0])

    def setModelData(self, editor, model, index):
        name_cell = index.siblingAtColumn(1)
        model.setData(index, f"{editor.currentText()} {name_cell.data()}")
