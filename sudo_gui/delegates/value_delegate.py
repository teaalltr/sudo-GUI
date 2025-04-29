"""
value_delegate.py
-----------------
Context-aware editor for the *Value* column in the Defaults tab.

• bool  → ['', 'true', 'false'] combo
• enum  → combo with the given choices
• int   → QSpinBox with min/max
• path/text → QLineEdit
• key == 'secure_path' → custom SecurePathWidget
"""

from __future__ import annotations

from typing import Any

from PyQt6.QtWidgets import (
    QStyledItemDelegate,
    QComboBox,
    QSpinBox,
    QLineEdit,
    QWidget,
)
from ..widgets.secure_path import SecurePathWidget
from ..constants import DEFAULTS_META


class ValueDelegate(QStyledItemDelegate):
    """Dynamic editor chosen from `DEFAULTS_META`."""

    # ------------------------------------------------------------------ #
    # Editor factory
    # ------------------------------------------------------------------ #
    def createEditor(self, parent, option, index):            # noqa: D401
        key: str = index.siblingAtColumn(0).data().strip()
        val: str = index.data().strip()
        meta: dict[str, Any] = DEFAULTS_META.get(key, {})
        kind: str = meta.get("type", "text")

        # ---- secure_path special widget --------------------------------
        if key == "secure_path":
            widget = SecurePathWidget(parent, val)
            widget.pathChanged.connect(lambda _: self.commitData.emit(widget))
            return widget

        # ---- ordinary kinds -------------------------------------------
        if kind == "bool":
            combo = QComboBox(parent)
            combo.addItems(["", "true", "false"])
            return combo

        if kind == "enum":
            combo = QComboBox(parent)
            combo.addItems(meta["choices"])
            return combo

        if kind == "int":
            spin = QSpinBox(parent)
            spin.setMinimum(meta.get("min", -99_999))
            spin.setMaximum(meta.get("max",  99_999))
            return spin

        # 'path' / 'text' fall-back
        return QLineEdit(parent)

    # ------------------------------------------------------------------ #
    # Data hand-off
    # ------------------------------------------------------------------ #
    def setEditorData(self, editor: QWidget, index):          # noqa: D401
        if isinstance(editor, SecurePathWidget):
            editor.line.setText(index.data())
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor: QWidget, model, index):    # noqa: D401
        if isinstance(editor, SecurePathWidget):
            model.setData(index, editor.value())
        else:
            super().setModelData(editor, model, index)
