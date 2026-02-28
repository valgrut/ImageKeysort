import dataclasses
from PyQt5.QtCore import QRect, QSize

from src.GalleryItem import GalleryItem


@dataclasses.dataclass
class CropData:
    imageData: GalleryItem
    cropRectangle: QRect
    originalImageSize: QSize
