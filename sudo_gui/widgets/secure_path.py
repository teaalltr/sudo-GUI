"""
secure_path.py
==============
A tiny in-place editor for the *secure_path* Defaults key:

* **SecurePathWidget** — a read-only QLineEdit plus a “…” button that pops
  the full *SecurePathDialog*.

* **SecurePathDialog** — lets the user build a colon-separated PATH by
  adding / re-ordering directories in a QListWidget.
"""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLineEdit,
)


# ------------------------------------------------------------------ #
#  Modal dialog
# ------------------------------------------------------------------ #
class SecurePathDialog(QDialog):
    """Modal list editor for `secure_path`."""

    def __init__(self, parent: QWidget | None = None, initial: str = "") -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit secure_path")
        self.resize(540, 320)

        main = QVBoxLayout(self)

        # ------------- centre piece: list + vertical buttons ----------
        hbox = QHBoxLayout()
        self.list = QListWidget(self)
        hbox.addWidget(self.list, 1)

        vbtns = QVBoxLayout()
        self.add_btn = QPushButton("Add…", self)
        self.rm_btn = QPushButton("Remove", self)
        self.up_btn = QPushButton("Up ▲", self)
        self.down_btn = QPushButton("Down ▼", self)

        for b in (self.add_btn, self.rm_btn, self.up_btn, self.down_btn):
            vbtns.addWidget(b)
        vbtns.addStretch(1)
        hbox.addLayout(vbtns)

        main.addLayout(hbox, 1)

        # ------------- OK / Cancel -----------------------------------
        bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        main.addWidget(bb)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)

        # ------------- signals ---------------------------------------
        self.add_btn.clicked.connect(self._add_path)
        self.rm_btn.clicked.connect(self._remove_selected)
        self.up_btn.clicked.connect(lambda: self._move(-1))
        self.down_btn.clicked.connect(lambda: self._move(+1))

        # ------------- populate --------------------------------------
        if initial:
            for p in initial.strip('"').split(":"):
                if p:
                    self.list.addItem(p)

    # ------------------------------------------------------------------ #
    # helper slots
    # ------------------------------------------------------------------ #
    def _add_path(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Choose directory")
        if (
            directory
            and all(
                self.list.item(i).text() != directory for i in range(self.list.count())
            )
        ):
            self.list.addItem(directory)

    def _remove_selected(self) -> None:
        for itm in self.list.selectedItems():
            self.list.takeItem(self.list.row(itm))

    def _move(self, delta: int) -> None:
        row = self.list.currentRow()
        if row == -1:
            return
        new_row = row + delta
        if 0 <= new_row < self.list.count():
            itm = self.list.takeItem(row)
            self.list.insertItem(new_row, itm)
            self.list.setCurrentRow(new_row)

    # ------------------------------------------------------------------ #
    # public result
    # ------------------------------------------------------------------ #
    @property
    def result(self) -> str:
        items = [self.list.item(i).text() for i in range(self.list.count())]
        joined = ":".join(items)
        return f'"{joined}"' if items else ""


# ------------------------------------------------------------------ #
#  Inline editor widget
# ------------------------------------------------------------------ #
class SecurePathWidget(QWidget):
    """
    Inline widget used by the *ValueDelegate*.

    Shows the current path in a read-only QLineEdit plus a button that
    launches the full SecurePathDialog. Emits **pathChanged(str)** when the
    user presses *OK* in the dialog.
    """

    pathChanged = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None, current: str = "") -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line = QLineEdit(current, self)
        self.line.setReadOnly(True)

        self.btn = QPushButton("…", self)
        self.btn.setFixedWidth(24)

        layout.addWidget(self.line, 1)
        layout.addWidget(self.btn)

        # signal
        self.btn.clicked.connect(self._edit)

    # ------------------------------------------------------------------ #
    # dialog launcher
    # ------------------------------------------------------------------ #
    def _edit(self) -> None:
        dlg = SecurePathDialog(self, self.line.text())
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.line.setText(dlg.result)
            self.pathChanged.emit(dlg.result)

    # ------------------------------------------------------------------ #
    # convenience for the delegate
    # ------------------------------------------------------------------ #
    def value(self) -> str:
        """Return the current secure_path string."""
        return self.line.text()
