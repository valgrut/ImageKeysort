import sys
import json
# from PIL import Image
# from tr import tr
from pathlib import Path
import shutil
from os import listdir
from os.path import isfile, join

from PyQt5.QtCore import QSize, Qt, QStringListModel
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QShortcut,
    QMenu,
    QAction,
)
from PyQt5.QtGui import QPixmap, QKeyEvent, QKeySequence

# pip3 install pyqt5
# pip3 install keyboard

width = 1152
height = 864

# TODO:
# - [ ] pridat kontrolu, ktere klavesy lze zmacknout (zablokovat napr. mezernik a bile znaky)
# - [ ] Pridat obrazek do imagewidgetu, kdyz neni nactena zadna src slozka.
# - [ ] Pridat nekam, jaka src slozka je aktualne nastavena
# - [ ] ! REFACTORING
# - [ ] Pridat counter (x/y), kolik obrazku zbyva v src slozce
# - [ ] Pridat moznost zobrazovat i gify (movie widget misto imageWidgetu)
# - [ ] ! Focus, abych mohl pouzivat sipky pro prochazeni obrazku
# - [ ] Pridat testy (make test)
# - [ ] Obrazek (label) by se mel zvetsit tak, aby zaplnil celou obrazovku, pokud zvetsim okno.
# - [ ] ! Kdyz neni otevrena zadna src slozka, tak moct kliknout na plochu, kde byvaji obrazky, pro otevreni dialogu vyberu src slozky.
# - [ ] Klikatko pro pridani a odstraneni zkratky / podzkratky
# - [ ] Po najeti na zkracenou cestu (napr. Images, Naruto, ...) se okamzite zobrazi cela cesta (v bubline).
# - [ ] Pridat Copy mode, aby se obrazek nepresunul, ale jen zkopiroval do dst.
# - [ ] Pridat zvyraznovani aktualne namacknute zkratky a filtraci - zustane pouze ta a jeji podzkratky.
# - [ ] Pridat zobrazeni i 3. vnoreni zkratek

allowed_keys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T, Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z]


class Shortcut():
    def __init__(self):
        pass


class ShortcutManager():
    def __init__(self):
        self.shortcut_manager = {"keys": {}}

    def printShortcuts():
        pass

    def add_shortcut(self, sequence):
        # TODO: toto je potreba dodelat a plnit ten dict behem Edit modu
        for category in sequence:
            if category in self.shortcut_manager:
                self.shortcut_manager.update({category: self.subcategory})

        print(self.shortcut_manager)

    def get_data(self):
        return self.shortcut_manager

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
        # print("last: ", last)
        return last["dst_path"]

    def add_key_under_current(self, current_key_ref, new_key):
        current_key_ref.update({new_key: {"dst_path": "", "keys": {}}})

    def _get_last_key_of_sequence_and_update(self, sequence):
        pre_current = self.shortcut_manager["keys"]
        current = self.shortcut_manager["keys"]
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
        pre_current = self.shortcut_manager["keys"]
        current = self.shortcut_manager["keys"]
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
        print("Ulozeno do data.json")
        with open('data.json', 'w', encoding='utf-8') as datafile:
            json.dump(self.shortcut_manager, datafile, ensure_ascii=False, indent=4)

    def load_shortcuts(self):
        print("Nactena data.json")
        with open('data.json', 'r', encoding='utf-8') as data:
            self.shortcut_manager = json.load(data)


class ImageGallery():
    # Bude handlovat gallery index v aktualne otevrene src slozce, nacitani dalsiho obrazku a pod.
    # Budu tak moct tuhle celou logiku vyjmout z MainWindow class.
    # TODO
    def __init__(self):
        pass
        


class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.label.setStyleSheet("background-color: yellow; border: 1px solid black; padding: 3px;")
        self.label.resize(900, 780)
        # self.pixmap = QPixmap(img_path)
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)

    def set_new_image(self, img_path):
        # TODO: Pokud .gif, tak movie, else pixmap
        self.pixmap.load(img_path)
        self.pixmap = self.pixmap.scaled(900, 770, Qt.KeepAspectRatio)
        self.label.setPixmap(self.pixmap)



# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quick Picture sorter")
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        main_layout = QHBoxLayout()
        left_inner_layout = QVBoxLayout()
        right_inner_layout = QVBoxLayout()

        main_window_widget = QWidget()
        main_window_widget.setLayout(main_layout)
        main_window_widget.setFocus(True)
        self.setCentralWidget(main_window_widget)

        self.shortcut_manager = ShortcutManager()

        # Add sub-layouts into the main layout
        main_layout.addLayout(left_inner_layout)
        main_layout.addLayout(right_inner_layout)

        self.image_filename_label = QLabel()
        # self.image_filename_label.resize(900, 10)
        self.image_filename_label.setMaximumHeight(25)
        # self.image_filename_label.setStyleSheet("background-color: green; border: 1px solid black; padding: 1px;")
        right_inner_layout.addWidget(self.image_filename_label)

        # Right side of the main layout
        self.imagewidget = ImageWidget()
        self.imagewidget.resize(self.imagewidget.sizeHint())
        self.imagewidget.setFocus(False)
        # TODO: Nez se nacte nejaka src dir, tak sem dat nejakej "empty" obrazek. Neco jako kruh, nejake opacity logo...
        # - Pridat moznost kliknout do toho prostoru pro zvoleni src slozky.
        # - Pouzit k tomu Resources
        right_inner_layout.addWidget(self.imagewidget)

        # TODO: Remove. [Just for DEBUG]: Manually setting src dir
        self.gallery_source_directory = "/home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/test/downloads"
        self.load_images()

        self.previous_image_button = QPushButton("&Previous", self)
        self.previous_image_button.clicked.connect(self.show_previous_image)
        self.previous_image_button.setFocus(False)

        self.next_image_button = QPushButton("&Next", self)
        self.next_image_button.clicked.connect(self.show_next_image)
        self.next_image_button.setFocus(False)

        right_control_buttons_layout = QHBoxLayout()
        right_control_buttons_layout.addWidget(self.previous_image_button)
        right_control_buttons_layout.addWidget(self.next_image_button)

        right_inner_layout.addLayout(right_control_buttons_layout)

        # Left side of the main layout
        self.key_label = QLabel("Key Sequence Pressed: None")
        self.key_label.resize(self.key_label.sizeHint())

        self.edit_button = QPushButton("&Edit", self)
        self.edit_button.clicked.connect(self.set_edit_mode)

        self.sort_button = QPushButton("&Sort", self)
        self.sort_button.clicked.connect(self.set_sort_mode)

        left_inner_button_layout = QHBoxLayout()
        left_inner_button_layout.addWidget(self.edit_button)
        left_inner_button_layout.addWidget(self.sort_button)

        left_inner_layout.addLayout(left_inner_button_layout)
        left_inner_layout.addWidget(self.key_label)

        # vars for history entries
        self.key_seq_history = []
        self.mv_history = []
        self.key_seq = ""
        self.permanent_key_seq = ""
        self.current_mode = "home" #dalsi: edit, sort
        print("Mod: " + self.current_mode)

        # Register global keyboard shortcuts:
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

        # Tree view for user's sorting shortcuts:
        self.tree = QTreeWidget()
        self.tree.setMaximumWidth(200)
        left_inner_layout.addWidget(self.tree)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Shortcut", "Directory"])
        self.tree.setEnabled(False)
        self.update_tree_view()

        # Create main Menu bar
        self._createActions()
        self._createMenuBar()
        self._connectActions()

    def _createMenuBar(self):
        menuBar = self.menuBar()

        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        # TODO: add "open source directory" option under File
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.openDirectoryAction)
        fileMenu.addAction(self.loadAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)

        editMenu = menuBar.addMenu("&Edit")

        # TODO: add "save / load" options for the data.json loading and saving

        helpMenu = menuBar.addMenu("&Help")
        # TODO: add info about project, add shortcuts

    def exitApp(self):
        #TODO: zjistit, jestli jsou zmeny v shortcuts a pripadne se zeptat, jestli ulozit
        print("Exiting")

        sys.exit(0)
        exit(0)

    def _createActions(self):
        self.openDirectoryAction = QAction("&open", self)
        self.saveAction = QAction("&save", self)
        self.loadAction = QAction("&load", self)
        self.exitAction = QAction("&exit", self)

    def _connectActions(self):
        self.openDirectoryAction.triggered.connect(self.set_source_directory)
        self.saveAction.triggered.connect(self.save_data)
        self.loadAction.triggered.connect(self.load_data)
        self.exitAction.triggered.connect(self.exitApp)


    def set_source_directory(self):
        self.gallery_source_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        print("Source directory:", self.gallery_source_directory)
        self.load_images()

    def load_images(self):
        if not self.gallery_source_directory:
            print("Error, src dir path is empty")
            return

        self.images = []
        self.images = [f for f in listdir(self.gallery_source_directory) if isfile(join(self.gallery_source_directory, f))]
        print(self.images)
        self.gallery_index = 0
        self.set_image()

    def show_next_image(self):
        if self.gallery_index < len(self.images) -1:
            self.gallery_index += 1
        print(f"DBG: new gallery_index: {self.gallery_index} out of {len(self.images) - 1}")
        self.set_image()


    def show_previous_image(self):
        if self.gallery_index >= 1:
            self.gallery_index -= 1
        print(f"DBG: new gallery_index: {self.gallery_index} out of {len(self.images) - 1}")
        self.set_image()

    def update_tree_view(self):
        # Just flush the whole content of the tree and rebuild it from scratch.
        self.tree.clear()
        items = []
        shortcuts_data = self.shortcut_manager.get_data()

        # TODO: add view for 3rd level of shortcuts, currently just 2 levels shown.
        for key, values in shortcuts_data["keys"].items():
            # print("Key a value", key, values)
            item = QTreeWidgetItem([key])
            # self.tree.expandItem(item)
            for subkey, subvalue in values["keys"].items():
                dst_path = subvalue["dst_path"]
                child = QTreeWidgetItem([subkey, Path(dst_path).name])
                item.addChild(child)
            items.append(item)

        self.tree.insertTopLevelItems(0, items)
        self.tree.expandAll()

    def save_data(self):
        self.shortcut_manager.save_shortcuts()

    def load_data(self):
        self.shortcut_manager.load_shortcuts()
        self.update_tree_view()

    def undo_last_operation(self):

        print("Undo last op")
        # print(self.mv_history)

        if not self.mv_history:
            return

        image_name = self.mv_history[-1]["image"]
        src = self.mv_history[-1]["dst"]
        dst = self.mv_history[-1]["src"]
        shutil.move(src + "/" + image_name, dst + "/" + image_name)

        # Remove current image from the list of images in src directory
        self.images.insert(0, image_name)

        # Remove last record from history
        if self.mv_history:
            self.mv_history.pop()

        # Show new image
        # self.set_image()


    def set_edit_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Edit")
        self.current_mode = "edit"
        self.edit_button.setStyleSheet("background-color: yellow;")
        self.sort_button.setStyleSheet("background-color: none;")

    def set_sort_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Sort")
        self.current_mode = "sort"
        self.edit_button.setStyleSheet("background-color: none;")
        self.sort_button.setStyleSheet("background-color: yellow;")

    def set_image(self):
        if self.gallery_index < 0:
            self.gallery_index = 0
        if self.gallery_index >= len(self.images):
            self.gallery_index = len(self.images) - 1

        if len(self.images) == 0:
            return

        self.imagewidget.set_new_image(str(Path(self.gallery_source_directory + "/" + self.images[self.gallery_index])))
        print(str(Path(self.gallery_source_directory + "/" + self.images[self.gallery_index])))
        self.image_filename_label.setText(f"{self.images[self.gallery_index]}")


    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent):
            pressed_key = event.text()
            print(pressed_key)

            # if self.current_mode == "home":
            if event.key() == Qt.Key_Left:
                self.show_previous_image()

            elif event.key() == Qt.Key_Right:
                self.show_next_image()

            elif event.key() == Qt.Key_Delete:
                pass

            else:
                pass

            # ==== EDIT MODE ====
            if self.current_mode == "edit":
                if event.key() == Qt.Key_Escape:
                    self.key_seq_history.append(self.key_seq)
                    self.key_seq = ""
                    # self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")
                    self.key_label.setText(f"Key Sequence Pressed: {self.permanent_key_seq}+{self.key_seq}")

                elif event.key() == Qt.Key_Return:
                    # Potvrdit zkratku - pak vyskoci dialog pro dst dir.
                    if self.key_seq:
                        for k in self.key_seq:
                            self.shortcut_manager.add_shortcut(self.key_seq)
                            if k == self.key_seq[-1]:
                                dst_sort_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
                                self.shortcut_manager.add_dst_path(self.key_seq, dst_sort_directory)
                                self.key_seq = ""
                                self.update_tree_view()
                                print(json.dumps(self.shortcut_manager.get_data(), indent=2))
                    else:
                        print("probably empty")


                else:
                    self.key_seq += pressed_key
                    self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")


            # ==== SORT MODE ====
            elif self.current_mode == "sort":
                # Cancel currently started shortcut or escape from the hold partial sequence
                if event.key() == Qt.Key_Escape:
                    print("ESC")
                    print("key_seq:", self.key_seq)
                    print("permanent_key_seq:", self.permanent_key_seq)
                    if self.key_seq and self.permanent_key_seq:
                        self.key_seq = ""
                    elif not self.key_seq and self.permanent_key_seq:
                        self.permanent_key_seq = ""
                    elif self.key_seq and not self.permanent_key_seq:
                        self.key_seq = ""
                    else:
                        pass
                    # self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")
                    self.key_label.setText(f"Key Sequence Pressed: {self.permanent_key_seq}+{self.key_seq}")

                # Hold current shortcut and use it as default for upcoming sequences until escape
                elif event.key() == Qt.Key_Return:  # Key_Return is non-numeric Enter key
                    print("ENTER")
                    print("b: key_seq:", self.key_seq)
                    print("b: permanent_key_seq:", self.permanent_key_seq)
                    if self.key_seq:
                        self.permanent_key_seq = self.key_seq
                        self.key_seq = ""
                    print("a: key_seq:", self.key_seq)
                    print("a: permanent_key_seq:", self.permanent_key_seq)
                    # self.key_seq = ""
                    # self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")

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
                        shutil.move(src + "/" + image_name, dst + "/" + image_name)

                        # Remove current image from the list of images in src directory
                        self.images.remove(image_name)

                        # Show new image
                        self.set_image()
                    else:
                        print("History is empty.")

                else:
                    if event.key() not in allowed_keys:
                        print("not a-z was pressed, nothing to append to shortcuts.")
                        return

                    self.key_seq += pressed_key

                    full_shortcut = ""
                    if self.permanent_key_seq:
                        full_shortcut = self.permanent_key_seq + self.key_seq
                    else:
                        full_shortcut = self.key_seq

                    print("key_seq:", self.key_seq)
                    print("full key_seq:", full_shortcut)

                    print("dst for shortcut:", self.shortcut_manager.get_dst_for_shortcut(full_shortcut))
                    if not self.key_seq:
                        return

                    # TODO: Zabranit, aby se obrazek presunul do slozky, pokud zkratka obsahuje sice dst cestu, ale i childrens.

                    if self.shortcut_manager.get_dst_for_shortcut(full_shortcut):
                        # self.key_label.setText(f"Key Sequence Pressed: {self.key_seq}")
                        self.key_seq_history.append(full_shortcut)

                        if not self.images:
                            print("Source directory is empty")
                            return

                        image_name = self.images[self.gallery_index]
                        src = self.gallery_source_directory
                        dst = self.shortcut_manager.get_dst_for_shortcut(full_shortcut)
                        print(f"Nalezeno, lze presunout z {self.gallery_source_directory} do {dst}!")

                        self.mv_history.append({"src": src, "dst": dst, "image": image_name})
                        shutil.move(src + "/" + image_name, dst + "/" + image_name)

                        # Remove current image from the list of images in src directory
                        self.images.remove(image_name)

                        # Show new image
                        self.set_image()

                        # Enable temporaly save and reuse partial shortcut
                        self.key_seq = ""

                        self.key_label.setText(f"Key Sequence Pressed: {self.permanent_key_seq}+{self.key_seq}")
                    else:
                        self.key_label.setText(f"Key Sequence Pressed: {self.permanent_key_seq}+{self.key_seq}")
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

