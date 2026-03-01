import logging

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QUndoCommand

log = logging.getLogger(__name__)


class CommandStack:
    def __init__(self):
        self._commands = []

    def clearStack(self):
        """
        Drop all command from the stack leaving it empty.
        """
        self._commands.clear()

    def empty(self) -> bool:
        return False if self._commands else True

    def count(self) -> int:
        """
        Get the number of commands in the stack.
        """
        return len(self._commands)

    def getCommandByFilename(self, filename: str) -> QUndoCommand | None:
        """
        Retrieve a command from the stack by its associated filename.
        """
        for cmd in self._commands:
            # if hasattr(cmd, 'imageName') and cmd.imageName == filename:
            if cmd.imageData.fileName == filename:
                return cmd
        return None

    def removeCommandByFilename(self, filename: str) -> bool:
        """
        Remove a command from the stack by its associated filename.
        """
        for i, cmd in enumerate(self._commands):
            # if hasattr(cmd, 'imageName') and cmd.imageName == filename:
            if cmd.imageData.fileName == filename:
                del self._commands[i]
                return True
        return False

    def getIndexOfCommandByFilename(self, filename: str) -> int:
        """
        Get the index of a specific command in the stack.
        """
        for i, cmd in enumerate(self._commands):
            # if hasattr(cmd, 'imageName') and cmd.imageName == filename:
            if cmd.imageData.fileName == filename:
                return i
        return -1

    def top(self) -> QUndoCommand | None:
        """
        Get the last command from the stack without removing it.
        """
        if self.count() > 0:
            return self._commands[-1]
        return None

    def pop(self) -> QUndoCommand | None:
        """
        Pop (and remove) the last command from the stack.
        """
        if self._commands:
            return self._commands.pop()
        return None

    def push(self, command: QUndoCommand) -> QUndoCommand:
        """
        Try to merge with existing or push a new command onto the stack.

        :returns pushed/merged command
        """

        # Try to find an existing (crop) command and if found, try to merge.
        # Why? Because user can adjust crop multiple times for the same image and
        #       we want to keep only the latest crop, so it can be reused for RepeatCrop().

        # TODO: Osetrit, ze je to stejny typ (tagging vs cropping vs ...)
        # if not isinstance(otherCommand, CropImageCommand):
        #     return False
        # if self.imageSrcPath != otherCommand.imageSrcPath:
        #     return False

        # TODO: Tohle ma byt genericke, ne jen pro Crop command!!!
        matchingCropCommand = self.getCommandByFilename(command.imageData.fileName)
        if matchingCropCommand:
            matchingCropCommand.mergeWith(command)
            return matchingCropCommand

        self._commands.append(command)

        return command

    def execute(self, command: QUndoCommand = None):
        if self.empty():
            log.info("Warning: CommandStack is empty, nothing to execute.")
            return

        if command is not None:
            command.execute()
            return

        self.top().execute()

    def undo(self, filename: str = None) -> bool:
        """
        Undo the last command or the command associated with the given filename.
        Removes the undone command from the stack.
        """
        if self.empty():
            log.info("Warning: CommandStack is empty, nothing to execute.")
            return False

        if filename is None:
            command = self.pop()
            command.undo()
            return True

        elif filename is not None:
            command = self.getCommandByFilename(filename)
            if command:
                command.undo()
                self.removeCommandByFilename(filename)
                return True

        return False
