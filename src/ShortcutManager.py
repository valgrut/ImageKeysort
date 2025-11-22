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

    def __init__(self, mainWindow, parent=None):
        super().__init__(parent)
        self.shortcutTree = {"keys": {}}
        self.mainWindow = mainWindow
        self.dataModified = False
        self.srcPathOfLoadedData = ""

    def areShortcutsModified(self) -> bool:
        return self.dataModified

    def setDataModified(self):
        self.dataModified = True
        print("MODIFIED")
        self.updateMainWindowTitleSignal.emit("*"+self.mainWindow.appTitle)

    def setDataUnmodified(self):
        self.dataModified = False
        self.updateMainWindowTitleSignal.emit(self.mainWindow.appTitle)

    def printShortcuts(self):
        pass

    def getAllPaths(self, shortcutsData) -> [str]:  # type: ignore
        """
        Recursively returns all dst_paths from the shortcuts json tree.
        """
        dstPathsList = []
        currentShortcutLevel = shortcutsData["keys"] # 'a', 'f', ...

        if currentShortcutLevel is None:
            return

        for key in currentShortcutLevel:
            # Add dst_path of the root key of this level into the list.
            dstPath = currentShortcutLevel[key]["dst_path"]
            if dstPath is not '':
                dstPathsList.append(dstPath)

            # Add dst paths of the sub-keys of the root key of this level.
            nextLevel = currentShortcutLevel[key]
            for returnedPath in self.getAllPaths(nextLevel):
                dstPathsList.append(returnedPath)

        return dstPathsList


    def isSomeDstDirectoryMissing(self, shortcutsData):
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

        return False


    def getData(self) -> dict[str, dict]:
        """
        Returns shortcuts data in the form of dictionary.
        """
        return self.shortcutTree


    # TODO: nevim, co to dela... mozna sem vlozit telo z _getLastKeyOfSequenceAndUpdate nebo to obecne nejak sjednotit.
    # metody rozdelit na public API a vnitrni logiku s _podtrzitkem za zacatku.
    def addShortcut(self, sequence):
        """
        Adds new shortcut into the shortcuts json tree.
        """
        # TODO: Co tohle sakra dela????? a subcategory neexistuje...
        currentNestLevel = self.shortcutTree
        for key in sequence:
            if key in currentNestLevel:
                self.shortcutTree.update({key: self.subcategory})
                self.setDataModified()
        print(json.dumps(self.shortcutTree))

        # Print nice json formatted TODO
        # print(self.shortcutTree["keys"])
        # print(json.dumps(self.shortcutTree))
        # print(json.dumps(sorted(self.shortcutTree, key=lambda x: x['keys'])))

    # TODO: Prejmenovat na addShortcutAndDstPath()
    def addDstPathForShortcut(self, sequence, dst_path):
        """
        Adds dst_path to the last key of the given sequence.

        Effectively it means that for the given sequence, dst_path is target path.
        """
        lastKey = self._getLastKeyOfSequenceAndUpdate(sequence)
        print("last_key:", lastKey)
        if lastKey:
            lastKey.update({"dst_path" : dst_path})
        else:
            print(f"Shortcut {sequence} has not been found.")


    def checkShortcutExists(self, sequence) -> bool:
        """
        Check whether the given shortcut sequence exists in the shortcuts json tree.

        :param sequence: Shortcut sequence to be checked.
        """
        lastKey = self.getLastKeyContentOfSequence(sequence)
        if lastKey:
            return True
        return False

    def addKeyUnderCurrent(self, currentKeyRef, new_key):
        """
        Adds new key under given key in the shortcuts json tree.

        :param currentKeyRef: Reference to the key under which the new key should be added.
        :param new_key: New key to be added.
        """
        currentKeyRef.update({new_key: {"dst_path": "", "keys": {}}})
        self.setDataModified()


    # TODO: Rename, protoze je to misleading. Myslel jsem, ze to vraci dstPath jakekoli existujici zkratky, ale ne, pouze pokud
    # je to longestMatch... !!!!!!!!!!!!!!
    # Peknej pojeb, kdyz jsem ji chtel pouzit pro parent's path advice, kdyz se pridava nova zkratka.
    def getDstPathForShortcut(self, sequence) -> str | None:
        """
        Returns dst_path for the last key of the given sequence.
        IF it is longest match!!!!!!!
        """
        print(f"get_dst_for_shortcut: {sequence}")
        lastKey = self.isSequenceLongestMatch(sequence)
        if not lastKey:
            log.warning("DEBUG: such sequence does not exist OR dst_path is empty OR shortcut is not longest match (contains children).")
            return None
        # print("last: ", last_key)
        # TODO: check jestli neni prazdny dst_path, myslel jsem, ze ten je tady uz osetreny, ale vraci v testu "", misto None.
        return lastKey["dst_path"]


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


    def isSequenceLongestMatch(self, sequence):
        """
        Return True only if the sequence is longest match, otherwise False.

        Example:
        lets have following structure:
        a
            b
                c
                    x

        We need to return True only if the sequence is "abc" and not "ab" or "a".
        Sequence is written by the user and for each key pressed, we need to check if the sequence is longest match.

        If it is not, user can "force" the usage of non-longest match by pressing "space" key.
        """
        lastKeyContent = self.getLastKeyContentOfSequence(sequence)

        # If key exists but have another sub-keys under the "keys", return False (Not longest match)
        # uz vim, proc to je- kdyz pisu zkratku, tak potrebuju, aby se to HITlo ne v prubehu, ale az kdyz
        # uz zkratka konci, ne treba u tretiho pismena z 5.
        if not lastKeyContent or lastKeyContent["keys"]:
            return False

        return lastKeyContent


    def _getLastKeyOfSequenceAndUpdate(self, sequence):
        """
        Get last key of sequence and if some keys are missing, add them to the shortcuts json tree.
        """
        preCurrent = self.shortcutTree["keys"]
        current = self.shortcutTree["keys"]
        for key in sequence:
            if key not in current.keys():
                print(f"Key {key} has not been found. Adding it.")
                self.addKeyUnderCurrent(current, key)

            # Go one key deeper into saved sequence
            preCurrent = current[key]
            current = current[key]["keys"]

        return preCurrent


    def getLastKeyContentOfSequence(self, sequence) -> str | None:
        """
        Get last key of sequence and does NOT matter whether the last key has children keys under itself.

        :param sequence:
        :return: Returns content of the last key of the sequence or False if the sequence does not exist.
        """
        nextAvailableKeys = self.shortcutTree["keys"]  # "keys": {a:, b:, x:}
        currentKeyContent = ""

        for key in sequence:
            print("Key", key)
            if key in nextAvailableKeys.keys():
                currentKeyContent = nextAvailableKeys[key]  # Content = {dst_path, keys:{}}
                nextAvailableKeys = currentKeyContent["keys"]
            else:
                print(f"DEBUG: such sequence does not exist.")
                return None

        return currentKeyContent


    def getLastKeyParent(self, keySequence: str):
        """
        if abc is sequence and key_char is 'c', return reference to 'b' key, so
        we can operate on the b's content. For example, remove c from b's keys.
        """
        
        # No parent for single key sequences
        if len(keySequence) < 2:
            return self.shortcutTree
        
        return self.getLastKeyContentOfSequence(keySequence[:-1])


    def moveShortcutSequence(self, sequence: str):
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
            print(f"DEBUG: Incorrect split string {isMatched}.")
            return False

        sequenceSplit = sequence.split(">")
        sourceSequence = sequenceSplit[0]
        destinationSequence = sequenceSplit[1]

        # Check existence of the source shortcut (before >)
        if not self.getLastKeyContentOfSequence(sourceSequence):
            print(f"Source shortcut ({sourceSequence}) does not exist.")
            self.updateStatusBarLabelSignal.emit(f"Source shortcut ({sourceSequence}) does not exist.")
            return False

        # Check existence of the target shortcut (after >)
        if len(destinationSequence) > 0 and not self.getLastKeyContentOfSequence(destinationSequence):
            print(f"To-be-moved shortcut ({destinationSequence}) does not exist.")
            self.updateStatusBarLabelSignal.emit(f"To-be-moved shortcut ({destinationSequence}) does not exist.")
            return False

        parentOfLastKey = self.getLastKeyParent(sourceSequence)

        # Check, whether resulting shortcut already does not exist
        resultingSequence = destinationSequence + sourceSequence[-1]
        if self.getLastKeyContentOfSequence(resultingSequence):
            print(f"Resulting shortcut ({resultingSequence}) does does already exist.")
            self.updateStatusBarLabelSignal.emit(f"Resulting shortcut ({resultingSequence}) does already exist.")
            return False

        # Remove last key of the sourceSequence from the shortcut tree
        poppedSubtree = None
        # if (sourceSequence in parentOfLastKey["keys"]):
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

        # TODO: dalsi focus problem po odstraneni zkratky a naslednem pridani... proc??
        return True


    def changeShortcutKeyChar(self, sequence: str):
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
        # TODO: check existenci menene src: if not shortcutExist(shortcut): return.
        isMatched = re.search("^[a-zA-Z1-9]+/[a-zA-Z1-9]$", sequence)

        if not isMatched:
            print(f"DEBUG: Incorrect change string {isMatched}.")
            return False

        sequenceSplit = sequence.split("/")
        sourceShortcut = sequenceSplit[0]
        keyCharToChange = sourceShortcut[-1]
        newKeyChar = sequenceSplit[1]

        # Check existence of the source shortcut (before /)
        if not self.getLastKeyContentOfSequence(sourceShortcut):
            print(f"Source shortcut ({sourceShortcut}) does not exist.")
            self.updateStatusBarLabelSignal.emit(f"Source shortcut ({sourceShortcut}) does not exist")
            return False

        # Check existence of the target shortcut (after /)
        targetSequence = sourceShortcut[:-1] + newKeyChar
        if self.getLastKeyContentOfSequence(targetSequence):
            print(f"Target shortcut ({targetSequence}) already exist.")
            self.updateStatusBarLabelSignal.emit(f"Target shortcut ({targetSequence}) already exist.")
            return False

        parentOfLastKey = self.getLastKeyParent(sourceShortcut)

        # Check, whether resulting shortcut already does not exist
        # TODO
        # resultingSequence = destinationSequence + sourceSequence[-1]
        # if self.getLastKeyContentOfSequence(resultingSequence):
        #     print(f"Resulting shortcut ({resultingSequence}) does does already exist.")
        #     self.updateStatusBarLabelSignal.emit(f"Resulting shortcut ({resultingSequence}) does already exist.")
        #     return False

        # Remove last key of the sourceSequence from the shortcut tree
        lastKeyChar = sourceShortcut[-1]
        changingKeyCharContent = parentOfLastKey["keys"].pop(lastKeyChar)
        self.setDataModified()

        # TODO: Tohle mozna nepotrebuju? Protoze to checkuju vyse... Mozna.
        # if keyCharToChange in parentOfLastKey["keys"]:
        #     print("ERROR: Such key char already exists under the parent key.")
        #     self.updateStatusBarLabelSignal.emit(f"Target shortcut ({targetSequence}) already exist.")
        #     return
        
        self.setDataModified()
        parentOfLastKey["keys"].update({newKeyChar: changingKeyCharContent})
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
            print(f"DEBUG: Incorrect split string {isMatched}.")
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

        # TODO: dalsi focus problem po odstraneni zkratky a naslednem pridani... proc??
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


    # def does_shortcut_exist(self, sequence) -> bool:
    #     last_key = _return_last_key_of_sequence(sequence)
    #     if last_key:
    #         return True
    #     return False


    def askSaveIfChanged(self) -> bool:
        """
        Asks user whether he wants to save changes in shortcuts if they are modified.
        """
        if not self.areShortcutsModified():
            return False

        qm = QMessageBox()
        ret = qm.question(self.mainWindow, '', "Do you want to save changes in shortcuts?", qm.Yes | qm.No)

        if ret == qm.No:
            print("DEBUG: Loading data without saving.")
            return False  # User does not want to save changes, but it is ok.

        if self.saveShortcuts():
            return False
        else:
            print("DEBUG: No file selected to save to. Abort.")
            return True


    def loadShortcutsFromFile(self, presetsFilePath) -> bool:
        if self.askSaveIfChanged():
            return False #TODO fix

        self._loadShortcuts(presetsFilePath)
        return True


    def loadShortcutsFromDialogue(self) -> bool:
        if self.askSaveIfChanged():
            return False

        jsonDataFile = QFileDialog.getOpenFileName(self.mainWindow, "Select file with shortcuts data to load.", self.srcPathOfLoadedData)

        self._loadShortcuts(jsonDataFile[0])
        return True


    def _loadShortcuts(self, presetsFilePath) -> bool:
        """
        Load shortcuts from json file.
        """

        if not presetsFilePath:
            print(f"No file selected.")
            return False

        try:
            with open(presetsFilePath, 'r', encoding='utf-8') as data:
                self.shortcutTree = json.load(data)
        except ValueError as error:
            # Prevent loading invalid json data
            print("DEBUG: Invalid json data!")
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

            # Print nonexisting paths:
            for path in nonexistingPaths:
                print("E: Directory does not exist: ", path)

        # Save path of the loaded data
        self.srcPathOfLoadedData = presetsFilePath

        self.setDataUnmodified()
        print(f"Data loaded from {presetsFilePath}.")
        self.updateStatusBarLabelSignal.emit(f"Data successfully loaded from {presetsFilePath}.")

        return True


    def saveShortcuts(self) -> bool:
        """
        User can save current shortcuts config any time. Whether they are modified or not does not matter.
        Because user could want to save current shortcuts just under different name.

        :return: True if saving was successful, False otherwise.
        """
        jsonDataFile = QFileDialog.getSaveFileName(self.mainWindow, "Select file or filename to save data into.", self.srcPathOfLoadedData)

        if not jsonDataFile[0]:
            print(f"No file selected.")
            return False

        with open(jsonDataFile[0], 'w', encoding='utf-8') as datafile:
            json.dump(self.shortcutTree, datafile, ensure_ascii=False, indent=4)
            # TODO: check jestli se spravne nabizi ta cesta po prvnim ulozeni pri dalsich ulozenich.

        self.srcPathOfLoadedData = jsonDataFile[0]
        self.setDataUnmodified()
        print(f"Data saved to {jsonDataFile}.")
        self.updateStatusBarLabelSignal.emit(f"Data saved to {jsonDataFile}.")

        return True


