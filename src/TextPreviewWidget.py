import logging
from pathlib import Path

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QKeyEvent, QMouseEvent, QTextCursor
from PyQt5.QtWidgets import QWidget, QStackedWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QMessageBox, \
    QVBoxLayout, QLineEdit, QPlainTextEdit

log = logging.getLogger(__name__)


class TextPreviewWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFocusPolicy(Qt.StrongFocus)
        self._maxBytes = 10000

    def setTextFile(self, path: str):
        bytesToRead = -1  # Default -1 = Read the whole file.

        # Prevent app freeze when reading very large text files.
        if Path(path).stat().st_size > self._maxBytes:
            bytesToRead = 10000

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            self.setPlainText(f.read(bytesToRead))
        self.moveCursor(QTextCursor.Start)