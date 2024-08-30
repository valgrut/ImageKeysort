import sys
import json
from PIL import Image
# from tr import tr
from pathlib import Path
import shutil

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QShortcut,
)
from PyQt5.QtGui import QPixmap, QKeyEvent, QKeySequence

# pip3 install pyqt5
# pip3 install keyboard

width = 1152
height = 864



# TODO:
# - [ ] pridat kontrolu, ktere klavesy lze zmacknout (zablokovat napr. mezernik a bile znaky)
# - [ ] Pridat label, ve kterem bude napsany aktualni Mod (sort, home, edit)



# shortcuts = {"keys": {"f": {"dst_path": "", "keys": {"b": {}}}}}
# print(json.dumps(shortcuts, indent=2))
# shortcuts["keys"]["f"].update({"dst_path": "/home/jpeska/Obrazky"})
# print(json.dumps(shortcuts, indent=2))
# shortcuts["keys"]["f"]["keys"]["b"].update({"dst_path": "/home/jpeska/Obrazky/ostatni"})
# print(json.dumps(shortcuts, indent=2))

# print(shortcuts["keys"]["f"]["keys"]["c"])

# exit(1)

class Shortcuts():
    def __init__(self):
        self.shortcuts = {"keys": {}}
        # self.shortcuts = {"keys": {"f": {"dst_path": "", "keys": {"b": {"dst_path": "", "keys": {}}}}}}

    def printShortcuts():
        pass

    def add_shortcut(self, sequence):
        # TODO: toto je potreba dodelat a plnit ten dict behem Edit modu
        for category in sequence:
            if category in self.shortcuts:
                self.shortcuts.update({category: self.subcategory})

        print(self.shortcuts)

    def get_data(self):
        return self.shortcuts

    def add_dst_path(self, sequence, dst_path):
        last_key = self._get_last_key_of_sequence_and_update(sequence)
        print("last_key:", last_key)
        if last_key:
            last_key.update({"dst_path" : dst_path})
        else:
            print(f"Zkratka {sequence} nebyla nalezena.")

    def removeShortcut():
        pass

    def get_dst_for_shortcut(self, sequence):
        last = self._get_last_key_of_sequence(sequence)
        if not last:
            return None
        return last["dst_path"]

    def add_key_under_current(self, current_key_ref, new_key):
        current_key_ref.update({new_key: {"dst_path": "", "keys": {}}})

    def _get_last_key_of_sequence_and_update(self, sequence):
        pre_current = self.shortcuts["keys"]
        current = self.shortcuts["keys"]
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
        pre_current = self.shortcuts["keys"]
        current = self.shortcuts["keys"]
        # print("Current: ", current)
        for key in sequence:
            # print("Sequence: ", sequence, "key:", key)
            if key not in current.keys():
                print(key, " nebyl nalezen")
                # self.add_key_under_current(current, key)
                return False

            # Go one key deeper into saved sequence
            pre_current = current[key]
            current = current[key]["keys"]

        return pre_current

    def does_shortcut_exist(self, sequence) -> bool:
        last_key = _return_last_key_of_sequence(sequence)
        if last_key:
            return True
        return False


    def save_shortcuts(self):
        with open('data.json', 'w', encoding='utf-8') as datafile:
            json.dump(self.shortcuts, datafile, ensure_ascii=False, indent=4)

    def load_shortcuts(self):
        with open('data.json', 'r', encoding='utf-8') as data:
            self.shortcuts = json.loads(data) #TODO fix this



class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)

    def set_new_image(self, img_path):
        self.pixmap = QPixmap(img_path)
        # self.pixmap = QPixmap('networking.jpg')
        self.label.setPixmap(self.pixmap)
        # self.resize(self.pixmap.width(), self.pixmap.height())

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quick Picture sorter")
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        layout = QHBoxLayout()

        widget = QWidget()
        widget.setLayout(layout)
        # Set the central widget of the Window.
        self.setCentralWidget(widget)

        self.shortcuts = Shortcuts()

        self.gallery_source_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        print(self.gallery_source_directory)
        self.images = []
        from os import listdir
        from os.path import isfile, join
        self.images = [f for f in listdir(self.gallery_source_directory) if isfile(join(self.gallery_source_directory, f))]
        print(self.images)
        self.gallery_index = 0

        # button1 = QPushButton("Press Me!")
        self.imagewidget = ImageWidget()
        self.imagewidget.set_new_image(str(Path(self.gallery_source_directory + "/" + self.images[self.gallery_index])))
        print(str(Path(self.gallery_source_directory + "/" + self.images[self.gallery_index])))

        # layout.addWidget(button1)
        self.key_label = QLabel("Key Sequence Pressed: None", widget)

        layout.addWidget(self.key_label)
        layout.addWidget(self.imagewidget)

        self.key_seq_history = []
        self.mv_history = []
        self.key_seq = ""
        self.current_mode = "home" #dalsi: edit, sort
        print("Mod: " + self.current_mode)

        set_edit_mode_seq = QKeySequence(Qt.CTRL + Qt.Key_E)
        self.set_edit_mode_shortcut = QShortcut(set_edit_mode_seq, self)
        self.set_edit_mode_shortcut.activated.connect(self.set_edit_mode)

        set_sort_mode_seq = QKeySequence(Qt.CTRL + Qt.Key_R)
        self.set_sort_mode_shortcut = QShortcut(set_sort_mode_seq, self)
        self.set_sort_mode_shortcut.activated.connect(self.set_sort_mode)

        undo_seq = QKeySequence(Qt.CTRL + Qt.Key_Z)
        self.undo_shortcut = QShortcut(undo_seq, self)
        self.undo_shortcut.activated.connect(self.undo_last_operation)
        
        save_data_seq = QKeySequence(Qt.CTRL + Qt.Key_S)
        self.save_data_shortcut = QShortcut(save_data_seq, self)
        self.save_data_shortcut.activated.connect(self.save_data)
        
        load_data_seq = QKeySequence(Qt.CTRL + Qt.Key_L)
        self.load_data_shortcut = QShortcut(load_data_seq, self)
        self.load_data_shortcut.activated.connect(self.load_data)

    def save_data(self):
        self.shortcuts.save_shortcuts()
    
    def load_data(self):
        self.shortcuts.load_shortcuts()

    def undo_last_operation(self):
        pass

    def set_edit_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Edit")
        self.current_mode = "edit"

    def set_sort_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Sort")
        self.current_mode = "sort"

    def set_image(self):
        if self.gallery_index < 0:
            self.gallery_index = 0
        if self.gallery_index >= len(self.images):
            self.gallery_index = len(self.images) - 1

        self.imagewidget.set_new_image(str(Path(self.gallery_source_directory + "/" + self.images[self.gallery_index])))
        print(str(Path(self.gallery_source_directory + "/" + self.images[self.gallery_index])))


    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent):
            pressed_key = event.text()
            print(pressed_key)

            if self.current_mode == "home":
                if event.key() == Qt.Key_Left:
                    self.gallery_index -= 1
                    self.set_image()

                if event.key() == Qt.Key_Right:
                    self.gallery_index += 1
                    self.set_image()

                if event.key() == Qt.Key_Delete:
                    pass

            elif self.current_mode == "edit":
                if event.key() == Qt.Key_Escape:
                    self.key_seq_history.append(self.key_seq)
                    self.key_seq = ""
                    self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")

                elif event.key() == Qt.Key_Return:
                    # Potvrdit zkratku - pak vyskoci dialog pro dst dir.
                    if self.key_seq:
                        for k in self.key_seq:
                            self.shortcuts.add_shortcut(self.key_seq)
                            if k == self.key_seq[-1]:
                                dst_sort_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
                                self.shortcuts.add_dst_path(self.key_seq, dst_sort_directory)
                                self.key_seq = ""
                                print(json.dumps(self.shortcuts.get_data(), indent=2))
                    else:
                        print("probably empty")


                else:
                    self.key_seq += pressed_key
                    self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")

                    # if pressed_key == "+":
                    #     print("")


            elif self.current_mode == "sort":
                if event.key() == Qt.Key_Escape:
                    self.key_seq = ""
                    self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")

                # Repeat last move from src to dst of current image.
                elif event.key() == Qt.Key_Period:
                    print("Repeat last finished command for current image")
                    if self.key_seq_history:
                        print(self.key_seq_history[-1])
                        # print(".......")
                        # print("from:", self.mv_history[-1]["src"])
                        # print("to", self.mv_history[-1]["dst"])

                        image_name = self.images[self.gallery_index]

                        src = self.mv_history[-1]["src"]
                        dst = self.mv_history[-1]["dst"]
                        shutil.move(src + "/" + image_name, dst)
                    else:
                        print("History is empty.")

                else:
                    self.key_seq += pressed_key
                    if self.shortcuts.get_dst_for_shortcut(self.key_seq):
                        # self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")
                        self.key_seq_history.append(self.key_seq)

                        print(f"Nalezeno, lze presunout z {self.gallery_source_directory} do {dst}!")
                        image_name = self.images[self.gallery_index]
                        src = self.gallery_source_directory
                        dst = self.shortcuts.get_dst_for_shortcut(self.key_seq)

                        self.mv_history.append({"src": src, "dst": dst, "image": image_name})
                        shutil.move(src + "/" + image_name, dst + "/" + image_name)

                        self.key_seq = ""
                        self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")
                    else:
                        self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")
            else:
                pass


    def parse_sequence(self):
        pass

    def dispatcher(self, key_pressed):
        # if hit() then move image from src to dst. and save sequence into history.
        pass

    # def change_mode(self):
    #     pass

def main():
    #img = Image.open("/home/jpeska/Downloads/7ton85.jpg")
    #img.show()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

