import json
import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import re


class ShortcutManager():
    def __init__(self, mainWindow):
        self.shortcutsData = {"keys": {}}
        self.mainWindow = mainWindow
        self.dataModified = False
        self.srcPathOfLoadedData = ""

    def areShortcutsModified(self) -> bool:
        return self.dataModified

    def setDataModified(self):
        self.dataModified = True
        print("MODIFIED")
        # TODO: tu se nastavi nekde '*' jako indikator ze data jsou modifikovana. Zatim:
        self.mainWindow.setWindowTitle("*"+self.mainWindow.appTitle)

    def setDataUnmodified(self):
        self.dataModified = False
        # TODO: tu se odnastavi nekde '*' jako indikator ze data nejsou zatim modifikovana. Zatim:
        self.mainWindow.setWindowTitle(self.mainWindow.appTitle)

    def printShortcuts(self):
        pass

    def getAllPaths(self, shortcutsData) -> []:
        dstPaths = []
        currentShortcutsLevel = shortcutsData["keys"] # 'a', 'f', ...

        if currentShortcutsLevel is None:
            return

        for shortcut in currentShortcutsLevel:
            # print("Shortcut", shortcut)

            dst = currentShortcutsLevel[shortcut]["dst_path"]
            # print("dst", dst)
            if dst is not '':
                dstPaths.append(dst)

            # Process nested shortcuts and add its dst into list
            nextLevel = currentShortcutsLevel[shortcut]
            # print("Next level", nextLevel)
            for returnedPath in self.getAllPaths(nextLevel):
                dstPaths.append(returnedPath)

        return dstPaths

    def isSomeDstDirectoryMissing(self, shortcutsData):
        nonexistingPaths = []

        # # DEBUG: Print all found paths
        # for path in self.getAllPaths(self.shortcutsData):
        #     print("dstpath", path)

        for path in self.getAllPaths(shortcutsData):
            if not os.path.exists(path):
                nonexistingPaths.append(path)

        if nonexistingPaths:
            return nonexistingPaths

        return False


    def addShortcut(self, sequence):
        # TODO: toto je potreba dodelat a plnit ten dict behem Edit modu
        for category in sequence:
            if category in self.shortcutsData:
                self.shortcutsData.update({category: self.subcategory})
                self.setDataModified()
        print(self.shortcutsData)

    def getData(self):
        return self.shortcutsData

    def addDstPath(self, sequence, dst_path):
        lastKey = self._getLastKeyOfSequenceAndUpdate(sequence)
        print("last_key:", lastKey)
        if lastKey:
            lastKey.update({"dst_path" : dst_path})
        else:
            print(f"Shortcut {sequence} has not been found.")

    def getDstForShortcut(self, sequence):
        print(f"get_dst_for_shortcut: {sequence}")
        lastKey = self.getLastPossibleKeyOfSequence(sequence)
        if not lastKey:
            return None
        # print("last: ", last_key)
        return lastKey["dst_path"]

    def addKeyUnderCurrent(self, currentKeyRef, new_key):
        currentKeyRef.update({new_key: {"dst_path": "", "keys": {}}})
        self.setDataModified()

    def _getLastKeyOfSequenceAndUpdate(self, sequence):
        preCurrent = self.shortcutsData["keys"]
        current = self.shortcutsData["keys"]
        # print("Current: ", current)
        for key in sequence:
            # print("Sequence: ", sequence, "key:", key)
            if key not in current.keys():
                print(f"Key {key} has not been found. Adding it.")
                self.addKeyUnderCurrent(current, key)

            # Go one key deeper into saved sequence
            preCurrent = current[key]
            current = current[key]["keys"]

        return preCurrent

    def getLastPossibleKeyOfSequence(self, sequence):
        current = self.shortcutsData["keys"]  # a, b, x, ...

        availableShortcuts = ""
        for key in sequence:
            print("Key", key)
            if key in current.keys():
                availableShortcuts = current[key]  # dst_path, keys
                print(key, "content", availableShortcuts)
                current = availableShortcuts["keys"]
            else:
                return False

        # If key exists but have another sub-keys under the "keys", return False (Not longest match)
        if "keys" not in availableShortcuts or availableShortcuts["keys"]:
            return False

        return availableShortcuts

    def _getLastKey(self, sequence):
        """
        Get last key of sequence and does NOT matter whether the key has children keys under itself.
        :param sequence:
        :return:
        """
        current = self.shortcutsData["keys"]  # a, b, x, ...

        currentKeyContent = ""
        for key in sequence:
            if key in current.keys():
                currentKeyContent = current[key]  # dst_path, keys
                current = currentKeyContent["keys"]
            else:
                return False

        # if "keys" not in currentKeyContent:
        #     return False

        return currentKeyContent

    # def does_shortcut_exist(self, sequence) -> bool:
    #     last_key = _return_last_key_of_sequence(sequence)
    #     if last_key:
    #         return True
    #     return False

    def askSaveIfChanged(self):
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
            print("DEBUG: Save was not successful.")
            return True


    def loadShortcuts(self) -> bool:
        if self.askSaveIfChanged():
            return False

        jsonDataFile = QFileDialog.getOpenFileName(self.mainWindow, "Select file with shortcuts data to load.", self.srcPathOfLoadedData)

        if not jsonDataFile[0]:
            print(f"No file selected.")
            return False

        try:
            with open(jsonDataFile[0], 'r', encoding='utf-8') as data:
                self.shortcutsData = json.load(data)
        except ValueError as error:
            # Prevent loading invalid json data
            print("DEBUG: Invalid json data!")
            self.mainWindow.statusBarLabel.setText(f"Error: Invalid json data in {jsonDataFile[0]}!")
            return False

        # Check that all destination directories exist for all loaded shortcuts
        nonexistingPaths = self.isSomeDstDirectoryMissing(self.shortcutsData)
        if nonexistingPaths:
            # TODO: Mozna jen warning do logu a zvyraznit cervene v Tree.
            for path in nonexistingPaths:
                # TODO: zde bude casem _append_ a pujde scrollovat tim logem.
                self.mainWindow.statusBarLabel.setText(f"Warning: One or more destination directories do not exist!")
                # TODO: Highlight all dst dirs that do not exist
            # return False

        # Print nonexisting paths:
        for path in nonexistingPaths:
            print("E: Directory does not exist: ", path)

        # Save path of the loaded data
        self.srcPathOfLoadedData = jsonDataFile[0]

        self.setDataUnmodified()
        print(f"Data loaded from {jsonDataFile}.")

        return True

    def saveShortcuts(self) -> bool:
        """
        User can save current shortcuts config any time. Whether they are modified or not does not matter.
        Because user could want to save current shortcuts just under different name.
        :return:
        """
        jsonDataFile = QFileDialog.getSaveFileName(self.mainWindow, "Select file or filename to save data into.", self.srcPathOfLoadedData)

        if not jsonDataFile[0]:
            print(f"No file selected.")
            return False

        with open(jsonDataFile[0], 'w', encoding='utf-8') as datafile:
            json.dump(self.shortcutsData, datafile, ensure_ascii=False, indent=4)
            # TODO: check jestli se spravne nabizi ta cesta po prvnim ulozeni pri dalsich ulozenich.

        self.srcPathOfLoadedData = jsonDataFile[0]
        self.setDataUnmodified()
        print(f"Saved to {jsonDataFile}.")

        return True

    def removeShortcutSequence(self, sequence: str):
        """
        Remove subtree marked by '-' in the sequence.

        Example:
        Lets Have following structure:
        a
            b
            c
                x
        Following options are possible:
        -a Removes the whole 'a' tree
        a-b Removes 'b' from the 'a' tree
        ac-x Removes 'x' from the 'c'.
        a-c Removes whole subtree of the 'c' key including the 'c'.

        :param sequence: Contains key sequence with '-' marking what should be removed from tree.
        :return:
        """

        isMatched = re.search("^[a-zA-Z1-9]*-[a-zA-Z1-9]$", sequence)

        if not isMatched:
            print(f"DEBUG: Incorrect split string {isMatched}.")
            return

        sequenceSplit = sequence.split("-")
        preDelimeter = sequenceSplit[0]
        postDelimeter = sequenceSplit[1]

        lastKey = ""
        if preDelimeter and postDelimeter:
            lastKey = self._getLastKey(preDelimeter)
        else:
            lastKey = self.shortcutsData

        if lastKey and (postDelimeter in lastKey["keys"]):
            if lastKey["keys"].pop(postDelimeter):
                self.setDataModified()

        # TODO: dalsi focus problem po odstraneni zkratky a naslednem pridani... proc??
        return True

    def clearShortcuts(self):
        self.shortcutsData = {"keys": {}}

