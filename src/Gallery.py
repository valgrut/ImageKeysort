import pathlib
from os import listdir
from os.path import isfile, join
import logging

from PyQt5 import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QMimeDatabase, QSize, QRect
from PyQt5.QtWidgets import QApplication, QFileDialog, QGraphicsDropShadowEffect, QStackedWidget, QRubberBand
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget

from src.EmptyGalleryWidget import EmptyGalleryImageWidget
from src.MediaContainerWidget import MediaContainerWidget
from src.CropData import CropData
from src.GalleryItem import GalleryItem

log = logging.getLogger(__name__)


class Gallery:
    """
    One specific gallery defined by source path.
    Gallery is opened in the Tabs.
    """

    def __init__(self):
        self.sourceDirectoryPath: pathlib.Path = None
        self.availableFiles: list[GalleryItem] = []
        self.currentFileIndex: int = -1  # Index with a value -1 represents empty gallery.
