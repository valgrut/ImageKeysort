from datetime import time
from pathlib import Path
from time import sleep

import pytesseract
import os
from PIL import Image
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from PyQt5.QtWidgets import QApplication, QWidget

# === Windows Issue ===
# Pycharm could not find the tesseract installation in the path, so installing manually:
# Windows: Installed from: https://github.com/UB-Mannheim/tesseract/wiki
# (https://github.com/tesseract-ocr/tesseract/releases/download/5.5.0/tesseract-ocr-w64-setup-5.5.0.20241111.exe)
# Installed into 'C:\Program Files\Tesseract-OCR\'


if os.name == "nt":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class TextExtractor(QWidget):

    updateStatusBarLabelSignal = pyqtSignal(str)

    def __init__(self, galleryManager):
        super().__init__()
        self.galleryManager = galleryManager

    @pyqtSlot()
    def extractTextFromImage(self):
        # TODO: maybe start an animation or something of loading (rotating circle)
        # TODO: Make this method asynchronous

        # OCR with pytesseract
        try:
            # text = pytesseract.image_to_string(Image.open(self.pixmap))

            # TODO: obrazek specifikovat Tady primo, nebo cestu vlozit do argumentu teto metody
            image_path = Path(self.galleryManager.getSourcePath(), self.galleryManager.getCurrentFilename())

            print("extractTextFromImage: ", image_path)
            self.updateStatusBarLabelSignal.emit(f"Text extraction started! Wait...")

            QApplication.processEvents()  # Force the processing of the emitted signal above

            text = pytesseract.image_to_string(Image.open(image_path), lang="ces+eng")

            # Copy to clipboard
            QApplication.clipboard().setText(text)
            # self.extractTextToClipboard_signal.emit(text)

            print()
            print("Extracted text copied to clipboard:")
            print("==================== TEXT ====================")
            print(text)
            print("==============================================")

            self.updateStatusBarLabelSignal.emit(f"Text extraction finished!")
        except Exception as e:
            print(e)
