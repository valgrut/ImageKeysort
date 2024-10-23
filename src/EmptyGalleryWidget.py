from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QCursor
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout

import resources_rc


class EmptyGalleryImageWidget(QWidget):

    selectSourceSignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            width: 100px;
            border: 1px solid black;
            border-radius: 10px;
            padding: 3px;
            background-color: rgb(100, 189, 189);
        """)

        icon = QPixmap(":/Resources/empty-inbox.png")
        icon = icon.scaled(200, 200, Qt.KeepAspectRatio)

        self.setCursor(QCursor(Qt.PointingHandCursor))

        self.label = QLabel()
        self.label.setPixmap(icon)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setToolTip("Click to select source directory of the gallery.")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)

        self.setLayout(self.layout)

    def mousePressEvent(self, event):
        self.selectSourceSignal.emit()
        if event.button() == Qt.LeftButton:
            print("EmptyGalleryImageWidget: Emitted (Left Click)")
        super().mousePressEvent(event)