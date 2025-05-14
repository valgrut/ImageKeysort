from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy

from src.Styles import Styles

class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet(f"""
            width: 100px;
            border: 1px solid black;
            border-radius: {Styles.widgetBorderRadius}px;
            padding: 3px;
            background-color: rgb(100, 100, 189);
        """)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setScaledContents(False)
        # self.label.setStyleSheet("""
        #     background-color: yellow;
        #     border: 1px solid black;
        #     border-radius: 20px;
        #     padding: 3px;
        #     """)
        # self.label.resize(900, 780)
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def updateImage(self, img_path):
        # TODO: Use cache?
        self.pixmap.load(img_path)
        self.updateScaledPixmap()

    def resizeEvent(self, event):
        self.updateScaledPixmap()
        super().resizeEvent(event)

    def updateScaledPixmap(self):
        if self.pixmap:
            scaledPixmap = self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaledPixmap)