from __future__ import annotations
from typing import Iterable, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton
)

# TODO: Rewrite to be more readable.

class TagSelectionDialog(QDialog):
    def __init__(self, tags: Iterable[str], parent=None, title: str = "Select tag"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        self._selected_tag: Optional[str] = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select tag (Arrows up/down, Enter = OK, Esc = Cancel):"))

        self.list = QListWidget(self)
        self.list.setSelectionMode(QListWidget.SingleSelection)
        self.list.setUniformItemSizes(True)

        for t in tags:
            self.list.addItem(QListWidgetItem(t))

        # Pokud jsou nějaké položky, předvyber první a dej fokus
        if self.list.count() > 0:
            self.list.setCurrentRow(0)
        self.list.setFocus()

        # Enter/dvojklik -> accept
        self.list.itemActivated.connect(self._accept_current)  # aktivace klávesou/klikem
        layout.addWidget(self.list)

        # Tlačítka (volitelné, ale užitečné pro UX)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn.clicked.connect(self._accept_current)
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.ok_btn)
        btn_row.addWidget(self.cancel_btn)
        layout.addLayout(btn_row)

        # Default akce Enter -> OK tlačítko
        self.ok_btn.setDefault(True)

        # Zajistí, že šipky a Enter fungují i kdyby se fokus ztratil na tlačítka
        self.setFocusPolicy(Qt.StrongFocus)

    def _accept_current(self):
        item = self.list.currentItem()
        if item is None:
            return
        self._selected_tag = item.text()
        self.accept()

    @staticmethod
    def selectTag(parent, tags: Iterable[str], title: str = "Select tag") -> Optional[str]:
        dlg = TagSelectionDialog(tags, parent=parent, title=title)
        result = dlg.exec_()
        if result == QDialog.Accepted:
            return dlg._selected_tag
        return None
