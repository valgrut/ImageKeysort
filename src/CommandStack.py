class CommandStack:
    def __init__(self):
        self._commands = []
        self._index = -1

    # def execute(self, command):
    #     # Remove any commands that are ahead of the current index
    #     del self._commands[self._index + 1:]
    #     command.execute()
    #     self._commands.append(command)
    #     self._index += 1

    def undo(self, filename: str = None):
        """
        Undo the last command or the command associated with the given filename.
        Removes the undone command from the stack.
        """
        if self.count() <= 0:
            return
        
        if filename is None:
            command = self.pop()
            command.undo()
            return

        elif filename is not None:
            command = self.getCommandByFilename(filename)
            if command:
                command.undo()
                self.removeCommandByFilename(filename)
                return
    
    def top(self):
        """
        Get the last command from the stack without removing it.
        """
        if self.count() > 0:
            return self._commands[-1]
        return None

    def push(self, command):
        """
        Push a new command onto the stack.
        """
        
        existingCommand = self.getCommandByFilename(command.imageName)

        # New command entry added, if not existing
        if not existingCommand:
            self._commands.append(command)
            return
        
        # Merge with existing command (Update cropRectangle)
        # Why? Because user can adjust crop multiple times for the same image and we want to keep only the latest crop, so it can be reused for RepeatCrop().
        existingCommand.cropRectangle = command.cropRectangle
        print(f"CHECK: {existingCommand.cropRectangle} updated to {command.cropRectangle}")
        idx = self.getIndexOfCommandByFilename(command.imageName)
        print(f"CHECK: Command in the list: {self._commands[idx].cropRectangle}")
        

    def pop(self):
        """
        Pop (and remove) the last command from the stack.
        """
        if self._commands:
            return self._commands.pop()
        return None
    
    def getCommandByFilename(self, filename: str):
        """
        Retrieve a command from the stack by its associated filename.
        """
        for cmd in self._commands:
            if hasattr(cmd, 'imageName') and cmd.imageName == filename:
                return cmd
        return None
    
    def removeCommandByFilename(self, filename: str):
        """
        Remove a command from the stack by its associated filename.
        """
        for i, cmd in enumerate(self._commands):
            if hasattr(cmd, 'imageName') and cmd.imageName == filename:
                del self._commands[i]
                return True
        return False

    def count(self):
        """
        Get the number of commands in the stack.
        """
        return len(self._commands)
    
    def getIndexOfCommandByFilename(self, filename: str):
        """
        Get the index of a specific command in the stack.
        """
        for i, cmd in enumerate(self._commands):
            if hasattr(cmd, 'imageName') and cmd.imageName == filename:
                return i
        return -1