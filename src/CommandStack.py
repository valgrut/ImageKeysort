import logging

from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtWidgets import QUndoCommand

log = logging.getLogger(__name__)


# TODO: Vetsina operaci tady musi byt prizpusobena hledani/odstranovani/returning tomu, aby se nasly vsechny commands ruznych typu pro dany 1 filename.
# TODO: Ale sakra, ja nechci udelat obsolete vsechny commands. Crop chci mit moznost pouzit na dalsi obrazek i kdyz predchozi jsem presunul jinam, sakra...


class CommandStack:
    def __init__(self):
        self._commands = []

    def clear(self):
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
            if cmd._fileData.fileName == filename:
                return cmd
        return None
    
    def getAllCommandsByFilename(self, filename: str) -> list[QUndoCommand] | None:
        """
        Retrieve all commands from the stack associated with given filename.
        """
        associatedCommands: list[QUndoCommand] = []
        for cmd in self._commands:
            # if hasattr(cmd, 'imageName') and cmd.imageName == filename:
            if cmd._fileData.fileName == filename:
                associatedCommands.append(cmd)
        return associatedCommands

    def getCommandOfSameType(self, filename: str, commandId: int) -> QUndoCommand | None:
        """
        Retrieve a command of the given ID from the stack by its associated filename.

        Used to get command of the specific type (TagCommand/CropCommand/...) for given filename.

        TODO WIP
        """
        for cmd in self._commands:
            # if hasattr(cmd, 'imageName') and cmd.imageName == filename:
            if cmd._fileData.fileName == filename and cmd.CMD_ID == commandId:
                return cmd
        return None

    def removeCommandByFilename(self, filename: str) -> bool:
        """
        Remove a command from the stack by its associated filename.
        """
        for i, cmd in enumerate(self._commands):
            # if hasattr(cmd, 'imageName') and cmd.imageName == filename:
            if cmd._fileData.fileName == filename:
                del self._commands[i]
                return True
        return False

    def getIndexOfCommandByFilename(self, filename: str) -> int:
        """
        Get the index of a specific command in the stack.
        
        TODO: 1. Rework to find by filename AND type
        TODO: 2. OR return ALL commands associated with this filename. !!! TODO TODO TODO !!!!!!!!!!!!!
        """
        for i, cmd in enumerate(self._commands):
            # if hasattr(cmd, 'imageName') and cmd.imageName == filename:
            if cmd._fileData.fileName == filename:
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

        matchingCommand = self.getCommandByFilename(command._fileData.fileName)
        if matchingCommand:
            log.info("Matching command found, trying to merge...")
            matchingCommand.mergeWith(command)
            return matchingCommand

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

    def disableRelatedCommands(self, filename: str):
        """
        Disable all commands associated with the provided filename.
        
        Required after moving the filename elsewhere, but in case of undoing the move operation, commands can be enabled again.
        
        # TODO: Ale sakra, ja nechci udelat obsolete vsechny commands. Crop chci mit moznost pouzit na dalsi obrazek i kdyz predchozi jsem presunul jinam, sakra...
        """
        for command in self._commands:
            if command._fileData.fileName == filename:
                command.setObsolete(True)

    def enableRelatedCommands(self, filename: str):
        """
        Enable all commands associated with the provided filename.
        
        Required after moving the filename back to its original src directory.
        """
        for command in self._commands:
            if command._fileData.fileName == filename:
                command.setObsolete(False)
