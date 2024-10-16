import json
from PyQt5.QtWidgets import QFileDialog


class ShortcutManager():
    def __init__(self, mainWindow):
        self.shortcutsData = {"keys": {}}
        self.mainWindow = mainWindow

    def printShortcuts(self):
        pass

    def add_shortcut(self, sequence):
        # TODO: toto je potreba dodelat a plnit ten dict behem Edit modu
        for category in sequence:
            if category in self.shortcutsData:
                self.shortcutsData.update({category: self.subcategory})

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

    def removeShortcut(self):
        pass

    def get_dst_for_shortcut(self, sequence):
        print(f"get_dst_for_shortcut: {sequence}")
        last_key = self._get_last_key_of_sequence(sequence)
        if not last_key:
            return None
        # print("last: ", last_key)
        return last_key["dst_path"]

    def add_key_under_current(self, current_key_ref, new_key):
        current_key_ref.update({new_key: {"dst_path": "", "keys": {}}})

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

    def _get_last_key_of_sequence(self, sequence):
        current = self.shortcutsData["keys"]  # a, b, x, ...

        currentKeyContent = ""
        for key in sequence:
            if key in current.keys():
                currentKeyContent = current[key]  # dst_path, keys
                current = currentKeyContent["keys"]

        # If key exists but does have another sub-keys under the "keys", return False (Not longest match)
        if currentKeyContent["keys"]:
            return False

        return currentKeyContent

    def does_shortcut_exist(self, sequence) -> bool:
        last_key = _return_last_key_of_sequence(sequence)
        if last_key:
            return True
        return False

    def load_shortcuts(self) -> bool:
        jsonDataFile = QFileDialog.getOpenFileName(self.mainWindow, "Select file with data")

        if not jsonDataFile[0]:
            print(f"No file selected.")
            return False

        with open(jsonDataFile[0], 'r', encoding='utf-8') as data:
            self.shortcutsData = json.load(data)

        print(f"Nactena data z {jsonDataFile}.")
        return True

    def save_shortcuts(self):
        jsonDataFile = QFileDialog.getSaveFileName(self.mainWindow, "Select file with data")
        with open(jsonDataFile[0], 'w', encoding='utf-8') as datafile:
            json.dump(self.shortcutsData, datafile, ensure_ascii=False, indent=4)
        print(f"Ulozeno do {jsonDataFile}.")
