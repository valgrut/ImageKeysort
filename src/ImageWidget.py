import pytesseract
import os
from PIL import Image
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy, QApplication
from src.Styles import Styles


# === Windows Issue ===
# Pycharm could not find the tesseract installation in the path, so installing manually:
# Windows: Installed from: https://github.com/UB-Mannheim/tesseract/wiki
# (https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe)
# Installed into 'C:\Program Files\Tesseract-OCR\'

if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class ImageWidget(QWidget):
    extractTextToClipboard_signal = pyqtSignal(str)

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
        self.currentImgPath = ""
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def updateImage(self, img_path):
        # TODO: Use cache?
        self.pixmap.load(img_path)
        self.currentImgPath = img_path
        self.updateScaledPixmap()

    def resizeEvent(self, event):
        self.updateScaledPixmap()
        super().resizeEvent(event)

    def updateScaledPixmap(self):
        if self.pixmap:
            scaledPixmap = self.pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(scaledPixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("Image clicked, extracting text...")

            # OCR with pytesseract
            try:
                # text = pytesseract.image_to_string(Image.open(self.pixmap))
                text = pytesseract.image_to_string(Image.open(self.currentImgPath), lang="ces+eng")

                # Copy to clipboard
                QApplication.clipboard().setText(text)
                # self.extractTextToClipboard_signal.emit(text)
                # self.appendStatus("Text extracted to clipboard")  # TODO notify user that text is copied

                print("Extracted text copied to clipboard:")
                print(text)
            except Exception as e:
                print(e)


