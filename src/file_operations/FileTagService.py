import re
import logging

from src.GalleryItem import GalleryItem

log = logging.getLogger(__name__)


class FileTagService:
    @staticmethod
    def verifyTag(tag: str):
        result = re.search(r"^\[[\w\s]+\]$", tag)
        return result

    @staticmethod
    def appendTag(fileItem: GalleryItem, tagToAdd: str) -> bool:
        """
        Allowed Tag format: "[a-zA-Z0-9_ ]+"
        """
        log.info(f"AppendTag Entered: \n{fileItem}\n{tagToAdd}")

        if not FileTagService.verifyTag(tagToAdd):
            log.info(f"Tag '{tagToAdd}' does not have a valid format.")
            return False

        if tagToAdd in fileItem.fileName:
            log.info(f"Filename already contains the tag '{tagToAdd}'.")
            return False

        currentFilePath = fileItem.pathAsPath()
        originalFilePath = currentFilePath
        currentFileNameNoExt = currentFilePath.stem
        extension = currentFilePath.suffix

        # finalTag = f" [{tagToAdd}]"
        finalTag = f" {tagToAdd}"
        nameWithTag = f"{currentFileNameNoExt}{finalTag}{extension}"
        fileItem.fileName = nameWithTag
        originalFilePath.rename(fileItem.pathAsPath())

        log.info(f"Tag added to the filename: {nameWithTag}")
        return True

    @staticmethod
    def removeTag(fileItem: GalleryItem, tagToRemove: str) -> bool:
        """
        Removes a tag TagToRemove from the filename, if such tag exists in the filename.
        That includes a 1 space before the tag.

        Allowed Tag format: "[a-zA-Z0-9_ ]+"
        """

        if not FileTagService.verifyTag(tagToRemove):
            log.info(f"Tag '{tagToRemove}' does not have a valid format.")
            return False

        if tagToRemove not in fileItem.fileName:
            log.info(f"Tag '{tagToRemove}'does not exist in the filename.")
            return False

        currentFilePath = fileItem.pathAsPath()
        originalFilePath = currentFilePath

        newName = fileItem.fileName.replace(" " + tagToRemove, '')
        # fileItem.fileName.replace(tagToRemove, '')
        fileItem.fileName = newName

        originalFilePath.rename(fileItem.pathAsPath())
        return True
