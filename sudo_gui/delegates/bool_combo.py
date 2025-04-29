"""
BoolComboDelegate
-----------------
Displays a **Yes/No/empty** drop-down for boolean *Defaults* keys.
"""

from PyQt6.QtWidgets import QStyledItemDelegate, QComboBox


class BoolComboDelegate(QStyledItemDelegate):
    """Shows a ['', 'true', 'false'] combo in an item view."""

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.addItems(["", "true", "false"])
        combo.setEditable(False)
        combo.currentIndexChanged.connect(self.commitData) 
        return combo

    def setEditorData(self, editor, index):             
        editor.setCurrentText(index.data())

    def setModelData(self, editor, model, index):         
        model.setData(index, editor.currentText())