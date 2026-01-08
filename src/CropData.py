import dataclasses
from PyQt5.QtCore import QRect, QSize


@dataclasses.dataclass(frozen=True)
class CropData:
    imageName: str
    imageSrcPath: str
    cropRectangle: QRect
    originalImageSize: QSize