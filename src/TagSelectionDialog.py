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


class TagSelectionDialog(QDialog):
    def __init__(self, tags: Iterable[str], parent=None, title: str = "Select tag"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        self._selectedTag: Optional[str] = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select tag (Arrows up/down, Enter = OK, Esc = Cancel):"))

        self.tagList = QListWidget(self)
        self.tagList.setSelectionMode(QListWidget.SingleSelection)
        self.tagList.setUniformItemSizes(True)

        # TODO: Sort tags alphabetically
        # TODO: Sort tags by usage frequency
        # TODO: Show (offer) only tags not already assigned to the image
        for tag in tags:
            # TODO: Load tags from file or settings, not hardcoded
            self.tagList.addItem(QListWidgetItem(tag))
        
        # Default selection to first item
        if self.tagList.count() > 0:
            self.tagList.setCurrentRow(0)
        self.tagList.setFocus()

        # Connect double-click or Enter key to accept
        self.tagList.itemActivated.connect(self._acceptCurrent)
        layout.addWidget(self.tagList)

        # Layout for buttons
        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch(1)
        
        self.okButton = QPushButton("OK")
        self.okButton.clicked.connect(self._acceptCurrent)
        self.okButton.setDefault(True)
        
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        
        buttonsLayout.addWidget(self.okButton)
        buttonsLayout.addWidget(self.cancelButton)
        layout.addLayout(buttonsLayout)

        self.setFocusPolicy(Qt.StrongFocus)


    def _acceptCurrent(self):
        item = self.tagList.currentItem()
        if item is None:
            return
        self._selectedTag = item.text()
        self.accept()


    @staticmethod
    def selectTag(parent, tags: Iterable[str], title: str = "Select tag to append") -> Optional[str]:
        dialogue = TagSelectionDialog(tags, parent=parent, title=title)
        result = dialogue.exec_()
        if result == QDialog.Accepted:
            return dialogue._selectedTag
        return None


    # TODO: N - add new tag
    # TODO: Del - delete selected tag
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_N:
            print("N pressed - Create new Tag")
            return

        return super().keyPressEvent(event)