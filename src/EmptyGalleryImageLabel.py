from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

import resources_rc


class EmptyGalleryImageLabel(QLabel):

    selectSourceSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        icon = QPixmap(":/Resources/empty-inbox.png")
        icon = icon.scaled(200, 200, Qt.KeepAspectRatio)
        self.setPixmap(icon)

    def mousePressEvent(self, event):
        self.selectSourceSignal.emit()
        if event.button() == Qt.LeftButton:
            print("Emitted")
        super().mousePressEvent(event)