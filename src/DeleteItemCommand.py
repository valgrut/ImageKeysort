import typing
from PyQt5.QtWidgets import QUndoCommand

# TODO: Separatni stack a commands pro
#   1. SortMode (move, delete, copy, Crop, ...)
#   2. Shortcuts ops (move shortcut, delete, add, change char, change dstpath, ...)

# Ref: https://doc.qt.io/qt-6/qundo.html
# Ref: https://doc.qt.io/qt-6/qundostack.html
# Ref: https://doc.qt.io/qt-6/qundocommand.html

class DeleteMediaCommand(QUndoCommand):
    def __init__(self):
        super().__init__()

    def undo(self) -> None:
        raise NotImplementedError

    def redo(self) -> None:
        raise NotImplementedError


class MoveMediaCommand(QUndoCommand):
    def __init__(self):
        super().__init__()

    def undo(self) -> None:
        raise NotImplementedError

    def redo(self) -> None:
        raise NotImplementedError


class CopyMediaCommand(QUndoCommand):
    def __init__(self):
        super().__init__()

    def undo(self) -> None:
        raise NotImplementedError

    def redo(self) -> None:
        raise NotImplementedError


class CropImageCommand(QUndoCommand):
    def __init__(self):
        super().__init__()

    def undo(self) -> None:
        raise NotImplementedError

    def redo(self) -> None:
        raise NotImplementedError
