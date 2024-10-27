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


    def add_shortcut(self, sequence):
        # TODO: toto je potreba dodelat a plnit ten dict behem Edit modu
        for category in sequence:
            if category in self.shortcutsData:
                self.shortcutsData.update({category: self.subcategory})
                self.setDataModified()
        print(self.shortcutsData)

    def get_data(self):
        return self.shortcutsData

    def add_dst_path(self, sequence, dst_path):
        last_key = self._get_last_key_of_sequence_and_update(sequence)
        print("last_key:", last_key)
        if last_key:
            last_key.update({"dst_path" : dst_path})
        else:
            print(f"Zkratka {sequence} nebyla nalezena.")

    def get_dst_for_shortcut(self, sequence):
        print(f"get_dst_for_shortcut: {sequence}")
        last_key = self.getLastPossibleKeyOfSequence(sequence)
        if not last_key:
            return None
        # print("last: ", last_key)
        return last_key["dst_path"]

    def add_key_under_current(self, current_key_ref, new_key):
        current_key_ref.update({new_key: {"dst_path": "", "keys": {}}})
        self.setDataModified()

    def _get_last_key_of_sequence_and_update(self, sequence):
        pre_current = self.shortcutsData["keys"]
        current = self.shortcutsData["keys"]
        # print("Current: ", current)
        for key in sequence:
            # print("Sequence: ", sequence, "key:", key)
            if key not in current.keys():
                print(key, " nebyl nalezen. Pridavam ho.")
                self.add_key_under_current(current, key)

            # Go one key deeper into saved sequence
            pre_current = current[key]
            current = current[key]["keys"]

        return pre_current

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

    def _get_last_key(self, sequence):
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

        if ret == qm.Yes:
            if self.save_shortcuts():
                return False  # TODO?
            else:
                print("DEBUG: Save was not successful.")
                return True  # TODO?
        else:  # qm.No:
            print("DEBUG: Loading data without saving.")
            return False  # User does not want to save changes, but it is ok.

    def load_shortcuts(self) -> bool:
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
        print(f"Nactena data z {jsonDataFile}.")

        return True

    def save_shortcuts(self) -> bool:
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
            # TODO: Pridat sem nabizenou cestu

        self.srcPathOfLoadedData = jsonDataFile[0]
        self.setDataUnmodified()
        print(f"Saved to {jsonDataFile}.")

        return True

    def removeShortcutSequence(self, sequence: str):
        """
        Remove subtree marked by '-' in the sequence. For example, for sequence "ac-d",
        remove 'd' subtree under the "ac".

        :param sequence: Contains key sequence with '-' marking what should be removed from tree.
        :return:
        """

        isMatched = re.search("^[a-z]*-[a-z]$", sequence)

        if not isMatched:
            print(f"DEBUG: Incorrect split string {isMatched}.")
            return

        sequenceSplit = sequence.split("-")
        preDelimeter = sequenceSplit[0]
        # print("Pre", preDelimeter)
        postDelimeter = sequenceSplit[1]
        # print("Post", postDelimeter)

        # print(self.shortcutsData)

        lastKey = ""
        if preDelimeter and postDelimeter:
            lastKey = self._get_last_key(preDelimeter)
        else:
            lastKey = self.shortcutsData

        # print("Last key (pre):", lastKey)
        if postDelimeter in lastKey["keys"]:
            if lastKey["keys"].pop(postDelimeter):
                self.setDataModified()

        # print("Last key (pos):", lastKey)

        # print("Remaining shortcuts", self.shortcutsData)

        return True

# TEST & DEBUG:
# sm = ShortcutManager("xxx")
# with open(r"C:\Users\Kyuubi\Repositories\WorkstationSetup\scripts\image-sorter\Presets\remove-test.json", 'r', encoding='utf-8') as data:
#     sm.shortcutsData = json.load(data)
# print(sm.removeShortcutSequence("ab-b"))
