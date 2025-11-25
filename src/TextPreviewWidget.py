import logging

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

    def setTextFile(self, path: str):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            self.setPlainText(f.read())
        self.moveCursor(QTextCursor.Start)