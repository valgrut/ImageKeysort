import shutil
import os

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint

from src.GalleryItem import GalleryItem
from src.file_operations.FileTagService import FileTagService


# TODO: How to handle the case, when tag is added from Selection, but removed by hand with normal rename???

# TODO: Finish command repeat on next file
# TODO: Fix Undo - multiple tags
# TODO: Fix mergeWith, to add multiple tags on one file.

class TagCommand(QUndoCommand):

    CMD_ID = 1003

    def __init__(self, fileData: GalleryItem, tag: str):
        super().__init__()
        self._fileData: GalleryItem = fileData
        self._addedTags: [str] = [tag]
        # self._addedTags.append(tag)

    def id(self) -> int:
        return self.CMD_ID

    def mergeWith(self, otherCommand: QUndoCommand) -> bool:
        """
        TODO finish
        """
        # if not isinstance(other, TagCommand):
        #     return False
        #
        # if self.imageName != other.imageName:
        #     return False
        #
        # # TODO: ??? Handle multiple tags?
        # return True
        raise NotImplementedError

    def execute(self):
        tagService = FileTagService()
        for tag in self._addedTags:
            tagService.appendTag(self._fileData, tag)

    def undo(self):
        """
        Remove all tags added through Tagging from the filename.
        """
        tagService = FileTagService()
        for tag in self._addedTags:
            tagService.removeTag(self._fileData, tag)

        self._addedTags.clear()
