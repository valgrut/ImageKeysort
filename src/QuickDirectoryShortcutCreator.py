from __future__ import annotations
from typing import Iterable, Optional

from PyQt5.QtCore import Qt
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
        self._shortcutField = QLineEdit()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter a name for new directory:"))
        layout.addWidget(self._directoryNameField)
        layout.addWidget(QLabel("Enter a shortcut for this directory:"))
        layout.addWidget(self._shortcutField)

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
    def enterName(parent) -> Optional[str]:
        dialogue = QuickDirectoryShortcutDialog(parent=parent)
        result = dialogue.exec_()
        if result == QDialog.Accepted:
            return dialogue._shortcutEntered, dialogue._directoryNameEntered
        return None