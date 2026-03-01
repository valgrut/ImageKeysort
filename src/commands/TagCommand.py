import shutil
import os
import logging

from PyQt5.QtWidgets import QUndoCommand
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QRect, QSize, QPoint

from src.GalleryItem import GalleryItem
from src.file_operations.FileTagService import FileTagService

log = logging.getLogger(__name__)

# TODO: How to handle the case, when tag is added from Selection, but removed by hand with normal rename???

# TODO: Finish command repeat on next file
# TODO: Fix execute from the stack, after push.

class TagCommand(QUndoCommand):

    CMD_ID = 1003

    def __init__(self, fileData: GalleryItem, tag: str):
        super().__init__()
        self._fileData: GalleryItem = fileData
        self._addedTags: [str] = [tag]

    def id(self) -> int:
        return self.CMD_ID

    def mergeWith(self, otherCommand: QUndoCommand) -> bool:
        """
        Merge current command with the provided one, keeping just the current one.
        """
        if not isinstance(otherCommand, TagCommand):
            log.info(f"Provided Command is not compatible to merge.")
            return False

        if self._fileData != otherCommand._fileData:
            log.info(f"Provided Command does not match one to merge.")
            return False

        for tag in otherCommand._addedTags:
            if tag not in self._addedTags:
                self._addedTags.append(tag)

        return True

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
