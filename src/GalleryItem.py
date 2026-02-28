from dataclasses import dataclass
import pathlib


@dataclass(order=True)
class GalleryItem:
    """
    Dataclass representing one picture/video/text file.

    This allows to pass reference to this object, and actions like renaming will happen everywhere.

    Initially, it was just string, so I would have to find and change this string on multiple
    places (in gallery's list, commands, ...) during the renaming, tagging, ...
    """
    fileName: str
    sourcePath: pathlib.Path

    def pathAsStr(self) -> str:
        """
        Return full path as a string.
        :return:
        """
        return str(self.sourcePath / pathlib.Path(self.fileName))

    def pathAsPath(self) -> pathlib.Path:
        """
        Return full path as a pathlib.Path.
        :return:
        """
        return self.sourcePath / pathlib.Path(self.fileName)

    # def __repr__(self):
    #     return f'{self.fileName}'
