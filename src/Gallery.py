import pathlib
import logging

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
