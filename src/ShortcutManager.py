import json
import os
import logging
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
import re

log = logging.getLogger(__name__)


class ShortcutManager(QObject):
    """
    Class representing and managing shortcuts data structure in the form of json tree.
    Also supports set of operations on the shortcuts data structure.

    TreeViewWidget is used to visualize this data structure.

    # Note: QObject is required for the Signals.

    # shortcut = "fbcd"
    # sequence = "f-b-c-d"
    """

    updateMainWindowTitleSignal = pyqtSignal(str)
    updateStatusBarLabelSignal = pyqtSignal(str)
    updateAvailableKeysLabelSignal = pyqtSignal()
    updateTreePreviewSignal = pyqtSignal()

    def __init__(self, mainWindow, parent=None):
        super().__init__(parent)
        self.shortcutTree = {"keys": {}}
        self._keyContent = {"dst_path": "", "keys": {}}
        self.mainWindow = mainWindow
        self.dataModified = False
        self.srcPathOfLoadedData = ""
        # self.operationsHistory = []

    def areShortcutsModified(self) -> bool:
        return self.dataModified

    def setDataModified(self):
        self.dataModified = True
        log.info("MODIFIED")
        self.updateMainWindowTitleSignal.emit("*"+self.mainWindow.appTitle)

    def setDataUnmodified(self):
        self.dataModified = False
        self.updateMainWindowTitleSignal.emit(self.mainWindow.appTitle)

    def printShortcuts(self):
        pass

    def getPossibleFollowupsKeychars(self, sequencePressed: str) -> list[str]:
        """
        For provided key-char sequence, return unsorted list of the keychars which are available next.
        """
        # log.info(f"Pressed sequence: {sequencePressed}")
        
        if not sequencePressed:
            childrenKeys = self.shortcutTree["keys"]
        
        elif self.shortcutExists(sequencePressed):
            # log.info(f"Data: {self.getLastKeyContentOfSequence(sequencePressed)["keys"].keys()}")
            childrenKeys = self.getLastKeyContentOfSequence(sequencePressed)["keys"].keys()
        
        else:
            childrenKeys = ["NONE"]

        # log.info(f"Final: {availableKeys}")
        
        return childrenKeys


    def getAllPaths(self, shortcutsData) -> [str]:  # type: ignore
        """
        Recursively returns all dst_paths from the shortcuts json tree.
        """
        dstPathsList = []
        currentShortcutLevel = shortcutsData["keys"]  # 'a', 'f', ...

        if currentShortcutLevel is None:
            return

        for key in currentShortcutLevel:
            # Add dst_path of the root key of this level into the list.
            dstPath = currentShortcutLevel[key]["dst_path"]
            if dstPath:  # is not '':
                dstPathsList.append(dstPath)

            # Add dst paths of the sub-keys of the root key of this level.
            nextLevel = currentShortcutLevel[key]
            for returnedPath in self.getAllPaths(nextLevel):
                dstPathsList.append(returnedPath)

        return dstPathsList


    def isSomeDstDirectoryMissing(self, shortcutsData) -> list[str]:
        """
        Check if all non-empty destination directories exist for all shortcuts.

        :param shortcutsData:
        :return: List of all non-existing paths.
        """
        nonexistingPaths = []

        for path in self.getAllPaths(shortcutsData):
            if not os.path.exists(path):
                nonexistingPaths.append(path)

        if nonexistingPaths:
            return nonexistingPaths

        return []


    def getData(self) -> dict[str, dict]:
        """
        Returns shortcuts data in the form of dictionary.
        """
        return self.shortcutTree


    def shortcutExists(self, shortcut: str) -> bool:
        """
        Check whether the given shortcut keychar sequence exists in the shortcuts json tree.

        Check, whether given keychar sequence exists in the json data tree. It does not
        matter, whether it has children keys or not.
        """

        currentKeyContent = self.shortcutTree

        if currentKeyContent is None or "keys" not in currentKeyContent:
            return False

        for keyChar in shortcut:
            currentKeyChildren = currentKeyContent["keys"]
            if keyChar not in currentKeyChildren:
                return False
            currentKeyContent = currentKeyChildren[keyChar]

        return True


    def shortcutExistsAndIsFinal(self, shortcut: str) -> bool:
        """
        Check, whether given shortcut exists and does not have any children keys.

        This is used during the typing of the shortcut, to avoid HITing in the
        middle of typing.

        Lets have existing shortcut "abc".
        If user types "ab", it should not HIT yet, because "ab" is not final
        shortcut, it has child "c".
        """

        if not self.shortcutExists(shortcut):
            return False

        lastKeyContent = self.getLastKeyContentOfSequence(shortcut)
        if lastKeyContent is None:
            return False

        if len(lastKeyContent["keys"].keys()) > 0:
            return False

        return True

    def getLastKeyContentOfSequence(self, shortcut: str) -> dict | None:
        """
        Returns content of the last key of the given shortcut sequence.

        Example:
        For shortcut "abc", it returns reference to "c" key content.
        Content of "c" key will have following structure:
        {
            "dst_path": "/some/path",
            "keys": {}
        }
        """

        if not self.shortcutExists(shortcut):
            return None

        currentKeyContent = self.shortcutTree

        # Travel to the end of the given shortcut in the data tree structure
        for keyChar in shortcut:
            currentKeyChildren = currentKeyContent["keys"]
            currentKeyContent = currentKeyChildren[keyChar]

        return currentKeyContent


    def getParentContentOfLastKeyOfSequence(self, shortcut: str) -> dict | None:
        """
        Returns reference to the parent of the last key of the given shortcut sequence.

        If shortcut is single key, it returns reference to the root of the shortcuts tree.

        Example:
        For shortcut "abc", it returns reference to "b" key content.
        Content of "b" key will have following structure:
        {
            "dst_path": "",
            "keys": {
                "c": {
                    "dst_path": "/some/path",
                    "keys": {}
                }
            }
        }

        Now we can operate on b's content, for example remove c from b's keys.
        """

        # No parent for single key sequences
        if len(shortcut) < 2:
            return self.shortcutTree

        return self.getLastKeyContentOfSequence(shortcut[:-1])


    def addShortcutSequence(self, shortcut: str, dst_path: str = "") -> None:
        """
        Adds new shortcut sequence into the shortcuts json tree.

        If dst_path is provided, it is set for the last key of the shortcut sequence.

        If key in the sequence already exists, it is not added again.
        """
        currentKeyContent = self.shortcutTree

        for keyChar in shortcut:
            currentKeyChildren = currentKeyContent["keys"]
            if keyChar not in currentKeyChildren:
                # currentKeyChildren.update({keyChar: self._keyContent.copy()})  # TODO deep copy required
                currentKeyChildren.update({keyChar: {"dst_path": "", "keys": {}}})  # workaround
                self.setDataModified()
            currentKeyContent = currentKeyChildren[keyChar]

        if dst_path:
            currentKeyContent["dst_path"] = dst_path
            self.setDataModified()

        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()


    def updateDstPathForShortcut(self, shortcut: str, dst_path: str) -> bool:
        """
        Updates dst_path for the last key of the given shortcut sequence.

        Before it was addDstPathForShortcut, but the 'update' is more accurate.

        If shortcut does not exist, returns False.
        """
        lastKeyContent = self.getLastKeyContentOfSequence(shortcut)
        if not lastKeyContent:
            return False

        lastKeyContent.update({"dst_path" : dst_path})
        self.setDataModified()
        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()
        return True


    def getDstPathForShortcut(self, shortcut: str) -> str | None:
        """
        Returns dst_path for the last key of the given shortcut sequence.

        If shortcut does not exist or dst_path is empty, returns None.
        """
        lastKeyContent = self.getLastKeyContentOfSequence(shortcut)
        if lastKeyContent and "dst_path" in lastKeyContent and len(lastKeyContent["dst_path"]) > 0:
            return lastKeyContent["dst_path"]

        return None


    def getFirstExistingDstPathFromParents(self, sequence) -> str | None:
        """
        Returns first dst_path it finds from the end of sequence to the first.
        Traverses up through parents and returns first non-empty dst_path.
        """
        remainingSequence = sequence[:-1]  # Remove the last, because it is the one for which we are finding dst_path.
        log.debug(f"remainingSequence: {remainingSequence}")

        while len(remainingSequence) > 0:
            content = self.getLastKeyContentOfSequence(remainingSequence)

            # When we add longer shortcut at once, last-key's parent does not exist yet. (And eventually nor parent's parent and so on)
            # So in this case, just go deeper into sequence.
            if content is None:
                remainingSequence = remainingSequence[:-1]
                continue

            if content["dst_path"]:
                return content["dst_path"]

            remainingSequence = remainingSequence[:-1]
        return None


    def moveShortcutSequence(self, sequence: str) -> bool:
        """
        Move key_char under different sub-tree.

        Syntax:
        [a-zA-Z]+>[a-zA-Z]*

        Example:
        Lets Have following structure:
        a
            b
            c
                x

        1. Move 'x' to the same level as 'a'
        acx>

        2. Move 'b' (and its subtree) under 'c'
        ab>ac

        """
        # TODO: Fix corner case: structura: a->c. Command: a>ac.  Sice validni syntax, ale nefunguje.
        # - Mozna check, ze char co se bude presouvat, (ten pred >) nesmi byt soucasti target (za >).
        isMatched = re.search("^[a-zA-Z1-9]+>[a-zA-Z1-9]*$", sequence)

        if not isMatched:
            log.info(f"DEBUG: Incorrect split string {isMatched}.")
            return False

        sequenceSplit = sequence.split(">")
        sourceSequence = sequenceSplit[0]
        destinationSequence = sequenceSplit[1]

        # Check existence of the source shortcut (before >)
        if not self.shortcutExists(sourceSequence):
            log.info(f"Source shortcut ({sourceSequence}) does not exist.")
            self.updateStatusBarLabelSignal.emit(f"Source shortcut ({sourceSequence}) does not exist.")
            return False

        # Check existence of the target shortcut (after >)
        if len(destinationSequence) > 0 and not self.shortcutExists(destinationSequence):
            log.info(f"To-be-moved shortcut ({destinationSequence}) does not exist.")
            self.updateStatusBarLabelSignal.emit(f"To-be-moved shortcut ({destinationSequence}) does not exist.")
            return False

        # Check, whether resulting shortcut already does not exist
        resultingSequence = destinationSequence + sourceSequence[-1]
        if self.shortcutExists(resultingSequence):
            log.info(f"Resulting shortcut ({resultingSequence}) does does already exist.")
            self.updateStatusBarLabelSignal.emit(f"Resulting shortcut ({resultingSequence}) does already exist.")
            return False

        # Remove last key and its content of the sourceSequence from the shortcut tree
        # if (sourceSequence in parentOfLastKey["keys"]):
        parentOfLastKey = self.getParentContentOfLastKeyOfSequence(sourceSequence)
        lastKeyChar = sourceSequence[-1]
        poppedSubtree = parentOfLastKey["keys"].pop(lastKeyChar)
        self.setDataModified()

        # Insert into new location
        destinationKey = None
        if destinationSequence:
            destinationKey = self.getLastKeyContentOfSequence(destinationSequence)
        else:
            destinationKey = self.shortcutTree
        destinationKey["keys"].update({lastKeyChar: poppedSubtree})

        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()
        return True


    def changeShortcutKeyChar(self, sequence: str) -> bool:
        """
        Move key_char under different sub-tree.

        Syntax:
        [a-zA-Z]+/[a-zA-Z]

        Example:
        Lets Have following structure:
        a
            b
            c
                x

        1. Change 'x' to 'f'
        acx/f
        """
        # TODO: Testy
        isMatched = re.search("^[a-zA-Z1-9]+/[a-zA-Z1-9]$", sequence)

        if not isMatched:
            log.info(f"DEBUG: Incorrect change string {isMatched}.")
            return False

        sequenceSplit = sequence.split("/")
        sourceShortcut = sequenceSplit[0]
        keyCharToChange = sourceShortcut[-1]
        newKeyChar = sequenceSplit[1]

        # Check existence of the source shortcut (before /)
        if not self.shortcutExists(sourceShortcut):
            log.info(f"Source shortcut ({sourceShortcut}) does not exist.")
            self.updateStatusBarLabelSignal.emit(f"Source shortcut ({sourceShortcut}) does not exist")
            return False

        # Check existence of the target shortcut (after /)
        targetSequence = sourceShortcut[:-1] + newKeyChar
        if self.shortcutExists(targetSequence):
            log.info(f"Target shortcut ({targetSequence}) already exist.")
            self.updateStatusBarLabelSignal.emit(f"Target shortcut ({targetSequence}) already exist.")
            return False

        parentOfLastKey = self.getParentContentOfLastKeyOfSequence(sourceShortcut)

        # Check, whether resulting shortcut already does not exist
        # TODO
        # resultingSequence = destinationSequence + sourceSequence[-1]
        # if self.getLastKeyContentOfSequence(resultingSequence):
        #     log.info(f"Resulting shortcut ({resultingSequence}) does does already exist.")
        #     self.updateStatusBarLabelSignal.emit(f"Resulting shortcut ({resultingSequence}) does already exist.")
        #     return False

        # Remove last key of the sourceSequence from the shortcut tree
        lastKeyChar = sourceShortcut[-1]
        changingKeyCharContent = parentOfLastKey["keys"].pop(lastKeyChar)
        self.setDataModified()

        # TODO: Tohle mozna nepotrebuju? Protoze to checkuju vyse... Mozna.
        # if keyCharToChange in parentOfLastKey["keys"]:
        #     log.info("ERROR: Such key char already exists under the parent key.")
        #     self.updateStatusBarLabelSignal.emit(f"Target shortcut ({targetSequence}) already exist.")
        #     return

        self.setDataModified()
        parentOfLastKey["keys"].update({newKeyChar: changingKeyCharContent})
        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()
        return True


    def removeShortcutSequence(self, sequence: str):
        """
        Remove subtree marked by '-' in the sequence.

        Syntax of the remove sequence:
        [a-z]*-[a-z]

        Example:
        Lets Have following structure:
        a
            b
            c
                x

        Following options are possible:
        -a Removes the whole 'a' shortcuts json tree.
        a-b Removes 'b' from the 'a' shortcuts json tree.
        ac-x Removes 'x' from the 'c'.
        a-c Removes whole subtree of the 'c' key including the 'c'.

        :param sequence: Contains key sequence with '-' marking what should be removed from shortcuts json tree.
        :return:
        """

        isMatched = re.search("^[a-zA-Z1-9]*-[a-zA-Z1-9]$", sequence)

        if not isMatched:
            log.info(f"DEBUG: Incorrect split string {isMatched}.")
            return False

        sequenceSplit = sequence.split("-")
        preDelimeter = sequenceSplit[0]
        postDelimeter = sequenceSplit[1]

        lastKey = ""
        if preDelimeter and postDelimeter:
            lastKey = self.getLastKeyContentOfSequence(preDelimeter)
        else:
            lastKey = self.shortcutTree

        if lastKey and (postDelimeter in lastKey["keys"]):
            if lastKey["keys"].pop(postDelimeter):
                self.setDataModified()
                return True

        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()
        return False


    def clearShortcuts(self):
        """
        Clears all shortcuts data.
        """
        if self.askSaveIfChanged():
            # No file selected to save into or other error occured.
            return
        self.setDataUnmodified()
        self.shortcutTree = {"keys": {}}
        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()


    def dropUnsavedChanges(self):
        """
        Loads previously loaded shortcuts data, effectively dropping all unsaved changes.
        """
        self._loadShortcuts(self.srcPathOfLoadedData)
        self.setDataUnmodified()
        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()


    def askSaveIfChanged(self) -> bool:
        """
        Asks user whether he wants to save changes in shortcuts if they are modified.
        """
        if not self.areShortcutsModified():
            return False

        qm = QMessageBox()
        ret = qm.question(self.mainWindow, '', "Do you want to save changes in shortcuts?", qm.Yes | qm.No)

        if ret == qm.No:
            log.info("DEBUG: Loading data without saving.")
            return False  # User does not want to save changes, but it is ok.

        if self.saveShortcuts():
            return False
        else:
            log.info("DEBUG: No file selected to save to. Abort.")
            return True


    def loadShortcutsFromFile(self, presetsFilePath) -> bool:
        if self.askSaveIfChanged():
            return False #TODO fix

        self._loadShortcuts(presetsFilePath)
        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()
        return True


    def loadShortcutsFromDialogue(self) -> bool:
        if self.askSaveIfChanged():
            return False

        jsonDataFile = QFileDialog.getOpenFileName(self.mainWindow, "Select file with shortcuts data to load.", self.srcPathOfLoadedData)

        self._loadShortcuts(jsonDataFile[0])
        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()
        return True


    def _loadShortcuts(self, presetsFilePath) -> bool:
        """
        Load shortcuts from json file.
        """
        
        if not presetsFilePath:
            log.info(f"No file selected.")
            return False

        try:
            with open(presetsFilePath, 'r', encoding='utf-8') as data:
                self.shortcutTree = json.load(data)
        except ValueError as error:
            # Prevent loading invalid json data
            log.info("DEBUG: Invalid json data!")
            self.updateStatusBarLabelSignal.emit(f"Error: Invalid json data in {presetsFilePath}!")
            return False

        # Check that all destination directories exist for all loaded shortcuts
        nonexistingPaths = self.isSomeDstDirectoryMissing(self.shortcutTree)
        if nonexistingPaths:
            # TODO: Mozna jen warning do logu a zvyraznit cervene v Tree.
            for path in nonexistingPaths:
                self.updateStatusBarLabelSignal.emit(f"Warning: One or more destination directories do not exist!")
                # TODO: Highlight all dst dirs that do not exist
            # return False

            # log.info nonexisting paths:
            for path in nonexistingPaths:
                log.info(f"E: Directory does not exist: {path}")

        # Save path of the loaded data
        self.srcPathOfLoadedData = presetsFilePath

        self.setDataUnmodified()
        log.info(f"Data loaded from {presetsFilePath}.")
        self.updateStatusBarLabelSignal.emit(f"Data successfully loaded from {presetsFilePath}.")
        self.updateTreePreviewSignal.emit()
        self.updateAvailableKeysLabelSignal.emit()
        return True


    def saveShortcuts(self) -> bool:
        """
        User can save current shortcuts config any time. Whether they are modified or not does not matter.
        Because user could want to save current shortcuts just under different name.

        :return: True if saving was successful, False otherwise.
        """
        jsonDataFile = QFileDialog.getSaveFileName(self.mainWindow, "Select file or filename to save data into.", self.srcPathOfLoadedData)

        if not jsonDataFile[0]:
            log.info(f"No file selected.")
            return False

        with open(jsonDataFile[0], 'w', encoding='utf-8') as datafile:
            json.dump(self.shortcutTree, datafile, ensure_ascii=False, indent=4)
            # TODO: check jestli se spravne nabizi ta cesta po prvnim ulozeni pri dalsich ulozenich.

        self.srcPathOfLoadedData = jsonDataFile[0]
        self.setDataUnmodified()
        log.info(f"Data saved to {jsonDataFile}.")
        self.updateStatusBarLabelSignal.emit(f"Data saved to {jsonDataFile}.")

        return True


