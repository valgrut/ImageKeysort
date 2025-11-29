from pathlib import Path
import logging

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

log = logging.getLogger(__name__)

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

            log.debug(f"Source path:       {self.galleryManager.getSourcePath()}")
            log.debug(f"Current file name: {self.galleryManager.getCurrentFilename()}")

            # TODO: obrazek specifikovat Tady primo, nebo cestu vlozit do argumentu teto metody?
            image_path = Path(self.galleryManager.getSourcePath(), self.galleryManager.getCurrentFilename())

            # Check if file exist (in case no gallery is opened yet)
            # if image_path == "." or not os.path.exists(image_path):
            if not self.galleryManager.getSourcePath() or not self.galleryManager.getCurrentFilename() or not os.path.exists(image_path):
                log.warning(f"Cannot extract text from the file '{image_path}'. Is source gallery opened?. Text extraction terminated.")
                raise FileNotFoundError
                return

            log.info(f"File for the text extraction: {image_path}.")
            self.updateStatusBarLabelSignal.emit(f"Text extraction started! Wait...")

            # Force the processing of the emitted signal above
            QApplication.processEvents()

            text = pytesseract.image_to_string(Image.open(image_path), lang="ces+eng")

            # Copy to clipboard
            QApplication.clipboard().setText(text)
            # self.extractTextToClipboard_signal.emit(text)

            print()
            print("Extracted text copied to clipboard!")
            print("==================== TEXT ====================")
            print(text)
            print("==============================================")
            # TODO Settings: Save extracted text into the file: "extractedTexts/{self.galleryManager.getCurrentFilename()}.txt"

            self.updateStatusBarLabelSignal.emit(f"Extraction finished! Text is in your clipboard.")
        except Exception as e:
            print(e)
