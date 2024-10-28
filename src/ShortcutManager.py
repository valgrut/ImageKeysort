import json
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

    def setDataUnmodified(self):
        self.dataModified = False

    def printShortcuts(self):
        pass

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

        currentKeyContent = ""
        for key in sequence:
            if key in current.keys():
                currentKeyContent = current[key]  # dst_path, keys
                current = currentKeyContent["keys"]

        # If key exists but have another sub-keys under the "keys", return False (Not longest match)
        if "keys" not in currentKeyContent or currentKeyContent["keys"]:
            return False

        return currentKeyContent

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

        if "keys" not in currentKeyContent:
            return False

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

        with open(jsonDataFile[0], 'r', encoding='utf-8') as data:
            self.shortcutsData = json.load(data)

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

        isMatched = re.search("^[a-z]*-[a-z]$", sequence)

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

        if postDelimeter in lastKey["keys"]:
            if lastKey["keys"].pop(postDelimeter):
                self.setDataModified()

        return True
