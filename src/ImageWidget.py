from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel


class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.label.setStyleSheet("""
            background-color: yellow;
            border: 1px solid black;
            border-radius: 20px;
            padding: 3px;
            """)
        self.label.resize(900, 780)
        # self.pixmap = QPixmap(img_path)
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)

    def updateImage(self, img_path):
        # TODO: Pokud .gif, tak movie, else pixmap
        self.pixmap.load(img_path)
        self.pixmap = self.pixmap.scaled(900, 770, Qt.KeepAspectRatio)
        self.label.setPixmap(self.pixmap)