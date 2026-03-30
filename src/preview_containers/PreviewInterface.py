from abc import ABC, abstractmethod
from src.GalleryItem import GalleryItem


class PreviewInterface(ABC):

    @abstractmethod
    def updatePreview(self, imageData: GalleryItem):
        pass
