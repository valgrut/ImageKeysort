from __future__ import annotations
from typing import Iterable, Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit
)


class QuickDirectoryShortcutDialog(QDialog):
    """
    Enter a new directory's name to be created in the sourceDirectory without need to use system's file manager.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter a name for new directory")
        self.setModal(True)

        self._directoryNameField = QLineEdit()
        self._directoryNamePixmap = QPixmap(':Resources/folder.png')
        self._directoryNameIcon = QLabel()
        self._directoryNameIcon.setPixmap(self._directoryNamePixmap.scaled(QSize(20, 20), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self._shortcutField = QLineEdit()
        self._shortcutPixmap = QPixmap(':Resources/font.png')
        self._shortcutIcon = QLabel()
        self._shortcutIcon.setPixmap(self._shortcutPixmap.scaled(QSize(20, 20), Qt.KeepAspectRatio, Qt.SmoothTransformation))

        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("Enter a name for new directory:"))
        row1 = QHBoxLayout(self)
        row1.addWidget(self._directoryNameIcon)
        row1.addWidget(self._directoryNameField)
        layout.addLayout(row1)
        
        layout.addWidget(QLabel("Enter a shortcut for this directory:"))
        row2 = QHBoxLayout(self)
        row2.addWidget(self._shortcutIcon)
        row2.addWidget(self._shortcutField)
        layout.addLayout(row2)

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
        self._directoryNameEntered = self._directoryNameField.text()
        self._shortcutEntered = self._shortcutField.text()
        self.accept()


    @staticmethod
    def enterName(parent) -> Optional[str] | None:
        dialogue = QuickDirectoryShortcutDialog(parent=parent)
        result = dialogue.exec_()
        if result == QDialog.Accepted:
            return dialogue._shortcutEntered, dialogue._directoryNameEntered
        return None, None