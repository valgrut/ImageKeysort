import logging

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QKeyEvent, QMouseEvent
from PyQt5.QtWidgets import QWidget, QStackedWidget, QLabel, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QMessageBox, \
    QVBoxLayout, QLineEdit

log = logging.getLogger(__name__)


class PdfPreviewWidget():
    def __init__(self, parent=None):
        super().__init__(parent)