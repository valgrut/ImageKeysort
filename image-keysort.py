import sys
import json
# from PIL import Image
# from tr import tr
from pathlib import Path
import shutil
import os
from os import listdir, makedirs
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
from PyQt5.QtGui import QPixmap, QKeyEvent, QKeySequence, QMovie

# pip3 install pyqt5
# pip3 install keyboard

width = 1152
height = 864

# Features DONE:
# - [x] Pridat nekam, jaka src slozka je aktualne nastavena
# - [x] Pridat zobrazeni i 3. vnoreni zkratek
# - [x] Pridat counter (x/y), kolik obrazku zbyva v src slozce
# - [x] pridat kontrolu, ktere klavesy lze zmacknout (zablokovat napr. mezernik a bile znaky)
# - [x] Pridat Copy mode, aby se obrazek nepresunul, ale jen zkopiroval do dst.
# - [x] Delete current image (Presune se do slozky TO_DELETE, kde si to pak uzivatel bude moct rucne smazat - to aby porad fungovala funkce Undo - nevim, jak bych to dostaval z kose).
#
# Features TODO:
# - [ ] Pridat obrazek do imagewidgetu, kdyz neni nactena zadna src slozka.
# - [~] ! REFACTORING
# - [~] Pridat moznost zobrazovat i gify (movie widget misto imageWidgetu)
# - [ ] Fix focus, abych mohl pouzivat sipky pro prochazeni obrazku
# - [ ] Pridat testy (make test)
# - [ ] Obrazek (label) by se mel zvetsit tak, aby zaplnil celou obrazovku, pokud zvetsim okno.
# - [ ] ! Kdyz neni otevrena zadna src slozka, tak moct kliknout na plochu, kde byvaji obrazky, pro otevreni dialogu vyberu src slozky.
# - [ ] Pridat moznost zvolit file se shortcuts pro nacteni, a pri ukladani tez.
#
# Shortcuts management:
# - [ ] Klikatko pro pridani a odstraneni zkratky / podzkratky
# - [ ] Po najeti na zkracenou cestu (napr. Images, Naruto, ...) se okamzite zobrazi cela cesta (v bubline).
# - [ ] Pridat zvyraznovani aktualne namacknute zkratky a filtraci - zustane pouze ta a jeji podzkratky.
# - [ ] FIX: searching longest path!
# - [ ] Edit mode: Pridat moznost odstranit nejakou zkratku, podzkratku ... (o-a) odstrani 'a' z 'o'.
#
#
# TODO: Promyslet:
# - Kdyz mam oi, kde je 'n', tak se bud provede vzdy az 'n', nebo pouze oi. Jak to udelat, aby bylo an vyber? Bude takova moznost?
# ze jakmile vytvorim podslozku, tak uz nepujde nic priradit do rodicovske slozky teto slozky? Jakoze, kdyz budu mit slozku Naruto ve slozce Anime, tak
# uz nic nepujde dat do Anime, ale pouze do dalsi podslozky? Pripadne, pridat moznost do configu nastavit casovy interval, po ktery pujde stisknout dodatecna klavesa, jinak se to presune do 'oa' ?

allowed_keys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T, Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z]


class Shortcut():
    def __init__(self):
        self.shortcut = ""
        self.dst_path = ""


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

#############################################################################
#############################################################################

# TODO: if gallery_empty or src_path not set: pixart = nejakej default obrazek.
class GalleryManager():
    def __init__(self, mainWindow):
        self.mainWindow = mainWindow # TODO: sig-slots
        self.images = []
        self.galleryIndex = 0
        self.sourceDirectoryPath = ""
        self.imageView = ImageWidget()  # for .png, .jpg, ...
        self.videoView = QMovie()  # for .gif and such

    def setSourcePath(self, path):
        self.sourceDirectoryPath = path
        self.mainWindow.source_dir_label.setText(path) # TODO: sig-slots
        self.loadImagesInDirectory()

    def getSourcePath(self) -> str:
        return self.sourceDirectoryPath

    def selectSourceDirectory(self):
        self.sourceDirectoryPath = QFileDialog.getExistingDirectory(self.mainWindow, "Select source directory")
        self.mainWindow.source_dir_label.setText(self.sourceDirectoryPath) # TODO: sig-slots
        self.loadImagesInDirectory()

    def loadImagesInDirectory(self):
        if not self.sourceDirectoryPath:
            # print("Msg: Error, src dir path is empty")
            self.selectSourceDirectory()

        self.images = []
        self.images = [f for f in listdir(self.sourceDirectoryPath) if isfile(join(self.sourceDirectoryPath, f))]
        self.images.sort()
        self.galleryIndex = 0
        # self.updatePreview()

    def isGalleryEmpty(self):
        if not self.images:
            return True
        return False

    def isCurrentVideo(self) -> bool:
        """
        returns true if current image is .gif or other video format
        """
        videoSuffixes = ("gif", "mp4", "avi")
        if str(self.images[self.galleryIndex]).endswith(videoSuffixes):
            return True
        return False

    def getGalleryIndex(self):
        return self.galleryIndex

    def incrementGalleryIndex(self):
        if self.galleryIndex < len(self.images) -1:
            self.galleryIndex += 1
        print(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.images) - 1}")

    def decrementGalleryIndex(self):
        if self.galleryIndex >= 1:
            self.galleryIndex -= 1
        print(f"DBG: new gallery_index: {self.galleryIndex} out of {len(self.images) - 1}")

    def setNextImage(self, viewLabel):
        self.incrementGalleryIndex()
        self.updatePreview(viewLabel) # TODO: sig-slots

    def setPreviousImage(self, viewLabel):
        self.decrementGalleryIndex()
        self.updatePreview(viewLabel) # TODO: sig-slots

    def getCurrentFilename(self):
        if self.images:
            return self.images[self.galleryIndex]
        return ""

    # TODO: previewLabel pryc, misto toho signal-slot
    def updatePreview(self, previewLabel):
        numOfImages = len(self.images)

        if numOfImages == 0:
            # TODO: sets something containing clickable board to open and set new source Directory.
            # self.previewLabel = ...?
            return

        if self.isCurrentVideo():
            # It is playable
            self.videoView.setFileName(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            previewLabel.setMovie(self.videoView)
            self.videoView.start()
        else:
            # It is image
            print(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            self.imageView.updateImage(str(Path(self.sourceDirectoryPath + "/" + self.images[self.galleryIndex])))
            previewLabel.setPixmap(self.imageView.pixmap)

        self.mainWindow.image_filename_label.setText(self.getCurrentFilename()) # TODO: sig-slots
        self.mainWindow.image_counter_label.setText(self.getCounterString()) # TODO: sig-slots

    def getCounterString(self) -> str:
        counter = str(self.galleryIndex + 1) + "/" + str(len(self.images))
        return counter

    def addFile(self, fileName, positionIndex=0):
        self.images.insert(positionIndex, fileName)

    def removeFile(self, fileName):
        if fileName in self.images:
            self.images.remove(fileName)

        if self.galleryIndex >= len(self.images):
            self.galleryIndex = len(self.images) - 1

#############################################################################
#############################################################################

class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.label.setStyleSheet("background-color: yellow; border: 1px solid black; padding: 3px;")
        self.label.resize(900, 780)
        # self.pixmap = QPixmap(img_path)
        self.pixmap = QPixmap()
        self.label.setPixmap(self.pixmap)

    def updateImage(self, img_path):
        # TODO: Pokud .gif, tak movie, else pixmap
        self.pixmap.load(img_path)
        self.pixmap = self.pixmap.scaled(900, 770, Qt.KeepAspectRatio)
        self.label.setPixmap(self.pixmap)


#############################################################################
#############################################################################

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

        # Add sub-layouts into the main layout
        main_layout.addLayout(left_inner_layout)
        main_layout.addLayout(right_inner_layout)

        self.source_dir_label = QLabel("Not selected")
        self.source_dir_label.setMaximumHeight(25)
        right_inner_layout.addWidget(self.source_dir_label)

        self.image_filename_label = QLabel()
        self.image_filename_label.setMaximumHeight(25)
        # self.image_filename_label.setStyleSheet("background-color: green; border: 1px solid black; padding: 1px;")
        right_inner_layout.addWidget(self.image_filename_label)

        # Management objects
        self.shortcut_manager = ShortcutManager()
        self.galleryManager = GalleryManager(self)
        # TODO: Remove. [Just for DEBUG]: Manually setting src dir
        self.galleryManager.setSourcePath("/home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/test/downloads")
        self.source_dir_label.setText(f"Source directory: {self.galleryManager.getSourcePath()}")

        # Right side of the main layout
        self.previewLabel = QLabel()
        self.previewLabel.setFocus(False)
        self.previewLabel.setStyleSheet("border: 1px solid blue;")
        # TODO: Nez se nacte nejaka src dir, tak sem dat nejakej "empty" obrazek. Neco jako kruh, nejake opacity logo...
        # - Pridat moznost kliknout do toho prostoru pro zvoleni src slozky.
        # - Pouzit k tomu Resources
        right_inner_layout.addWidget(self.previewLabel)

        self.previous_image_button = QPushButton("&Previous", self)
        self.previous_image_button.clicked.connect(self.showPreviousImage)
        self.previous_image_button.setFocus(False)
        self.previous_image_button.setStyleSheet("width: 150px;")

        self.next_image_button = QPushButton("&Next", self)
        self.next_image_button.clicked.connect(self.showNextImage)
        self.next_image_button.setFocus(False)
        self.next_image_button.setStyleSheet("width: 150px;")

        self.image_counter_label = QLabel()
        self.image_counter_label.setText("0/0")

        right_control_buttons_layout = QHBoxLayout()
        right_control_buttons_layout.addWidget(self.previous_image_button)
        right_control_buttons_layout.addStretch()
        right_control_buttons_layout.addWidget(self.image_counter_label)
        right_control_buttons_layout.addStretch()
        right_control_buttons_layout.addWidget(self.next_image_button)

        right_inner_layout.addLayout(right_control_buttons_layout)

        self.statusBarLabel = QLabel("Status bar")
        self.statusBarLabel.setMaximumHeight(25)
        self.statusBarLabel.setStyleSheet("border: 1px solid black;")
        right_inner_layout.addWidget(self.statusBarLabel)


        # Left side of the main layout
        self.key_label = QLabel("Key Sequence Pressed: None")
        self.key_label.resize(self.key_label.sizeHint())

        self.copy_button = QPushButton("&Copy", self)
        self.copy_button.clicked.connect(self.toggleCopyMode)

        self.edit_button = QPushButton("&Edit", self)
        self.edit_button.clicked.connect(self.set_edit_mode)

        self.sort_button = QPushButton("&Sort", self)
        self.sort_button.clicked.connect(self.set_sort_mode)

        left_inner_button_layout = QHBoxLayout()
        left_inner_button_layout.addWidget(self.edit_button)
        left_inner_button_layout.addWidget(self.sort_button)

        left_inner_layout.addWidget(self.copy_button)
        left_inner_layout.addLayout(left_inner_button_layout)
        left_inner_layout.addWidget(self.key_label)

        # vars for history entries
        self.key_seq_history = []
        self.mv_history = []
        self.key_seq = ""
        self.permanent_key_seq = ""
        self.current_mode = "home" #dalsi: edit, sort
        self.copyOnly = False
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

        toggle_copy_seq = QKeySequence(Qt.CTRL + Qt.Key_C)
        self.toggle_copy_shortcut = QShortcut(toggle_copy_seq, self)
        self.toggle_copy_shortcut.activated.connect(self.toggleCopyMode)

        # Tree view for user's sorting shortcuts:
        self.tree = QTreeWidget()
        self.tree.setMaximumWidth(200)
        left_inner_layout.addWidget(self.tree)
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Shortcut", "Directory"])
        self.tree.setEnabled(False)
        self.update_tree_view()

        # Update Counter label
        self.image_counter_label.setText(self.galleryManager.getCounterString())

        # Create main Menu bar
        self._createActions()
        self._createMenuBar()
        self._connectActions()

        self.galleryManager.updatePreview(self.previewLabel)

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
        self.openDirectoryAction.triggered.connect(self.galleryManager.selectSourceDirectory)
        self.saveAction.triggered.connect(self.save_data)
        self.loadAction.triggered.connect(self.load_data)
        self.exitAction.triggered.connect(self.exitApp)

    # def setStatusBarMessage(self, message):
    #     self.statusBarLabel.setText(message)

    def showNextImage(self):
        self.galleryManager.setNextImage(self.previewLabel)
        self.image_counter_label.setText(self.galleryManager.getCounterString())

    def showPreviousImage(self):
        self.galleryManager.setPreviousImage(self.previewLabel)
        self.image_counter_label.setText(self.galleryManager.getCounterString())

    def update_tree_view(self):
        # Just flush the whole content of the tree and rebuild it from scratch.
        self.tree.clear()
        items = []
        shortcuts_data = self.shortcut_manager.get_data()

        for key_L1, values_L1 in shortcuts_data["keys"].items():
            # print("Key a value", key, values)
            item_L1 = QTreeWidgetItem([key_L1])
            # self.tree.expandItem(item)
            for key_L2, values_L2 in values_L1["keys"].items():
                item_L2 = QTreeWidgetItem([key_L2])
                for key_L3, values_L3 in values_L2["keys"].items():
                    item_L3 = QTreeWidgetItem([key_L3])
                    dst_path = values_L3["dst_path"]
                    child = QTreeWidgetItem([key_L3, Path(dst_path).name])
                    item_L2.addChild(child)
                item_L1.addChild(item_L2)
            items.append(item_L1)

        # for key, values in shortcuts_data["keys"].items():
        #     # print("Key a value", key, values)
        #     item = QTreeWidgetItem([key])
        #     # self.tree.expandItem(item)
        #     for subkey, subvalue in values["keys"].items():
        #         # TODO
        #         dst_path = subvalue["dst_path"]
        #         child = QTreeWidgetItem([subkey, Path(dst_path).name])
        #         item.addChild(child)
        #     items.append(item)

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
        positionIndex = self.mv_history[-1]["gallery_index"]
        shutil.move(src + "/" + image_name, dst + "/" + image_name)
        self.statusBarLabel.setText(f"File moved BACK From: {src} to {dst}.")

        # Remove current image from the list of images in src directory
        self.galleryManager.addFile(image_name, positionIndex)

        # Update counter label
        self.image_counter_label.setText(self.galleryManager.getCounterString())

        # Remove last record from history
        if self.mv_history:
            self.mv_history.pop()

        # Show new image
        self.galleryManager.updatePreview(self.previewLabel)
        # print(self.images)

    def toggleCopyMode(self):
        if self.copyOnly is False:
            print("Current mode: Copy")
            self.copyOnly = True
            self.copy_button.setStyleSheet("background-color: yellow;")
            return

        if self.copyOnly is True:
            print("Current mode: Move")
            self.copyOnly = False
            self.copy_button.setStyleSheet("background-color: none;")
            return


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


    def keyPressEvent(self, event):
        if isinstance(event, QKeyEvent):
            pressed_key = event.text()
            print(pressed_key)

            # if self.current_mode == "home":
            if event.key() == Qt.Key_Left:
                self.showPreviousImage()

            elif event.key() == Qt.Key_Right:
                self.showNextImage()

            elif event.key() == Qt.Key_Delete:
                pass

            else:
                pass

            # TODO: Refactor following if-else hell:  !!!!!!!!!!!!!
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
                    # print("key_seq:", self.key_seq)
                    # print("permanent_key_seq:", self.permanent_key_seq)
                    if self.key_seq and self.permanent_key_seq:
                        self.key_seq = ""
                    elif not self.key_seq and self.permanent_key_seq:
                        self.permanent_key_seq = ""
                    elif self.key_seq and not self.permanent_key_seq:
                        self.key_seq = ""
                    else:
                        pass
                    self.key_label.setText(f"Key Sequence Pressed: {self.permanent_key_seq}+{self.key_seq}")

                # Hold current shortcut and use it as default for upcoming sequences until escape
                elif event.key() == Qt.Key_Return:  # Key_Return is non-numeric Enter key
                    print("ENTER")
                    # print("b: key_seq:", self.key_seq)
                    # print("b: permanent_key_seq:", self.permanent_key_seq)
                    if self.key_seq:
                        self.permanent_key_seq = self.key_seq
                        self.key_seq = ""
                    # print("a: key_seq:", self.key_seq)
                    # print("a: permanent_key_seq:", self.permanent_key_seq)
                    # self.key_seq = ""
                    self.key_label.setText(f"Key Sequence Pressed: {self.permanent_key_seq}+{self.key_seq}")

                # Repeat last move from src to dst of current image.
                elif event.key() == Qt.Key_Period:
                    print("Repeat last finished command for current image")
                    if self.key_seq_history:
                        print(self.key_seq_history[-1])
                        # print(".......")
                        # print("from:", self.mv_history[-1]["src"])
                        # print("to", self.mv_history[-1]["dst"])

                        image_name = self.galleryManager.getCurrentFilename()

                        src = self.mv_history[-1]["src"]
                        dst = self.mv_history[-1]["dst"]

                        # Remove current image from the list of images in src directory
                        if not self.copyOnly:
                            self.galleryManager.removeFile(image_name)
                            shutil.move(src + "/" + image_name, dst + "/" + image_name)
                            self.statusBarLabel.setText(f"File moved From: {src} to {dst}.")
                        else:
                            shutil.copy2(src + "/" + image_name, dst + "/" + image_name)
                            self.galleryManager.incrementGalleryIndex()
                            self.statusBarLabel.setText(f"File copied From: {src} to {dst}.")

                        # Update counter label
                        self.image_counter_label.setText(self.galleryManager.getCounterString())

                        # Show new image
                        self.galleryManager.updatePreview(self.previewLabel)
                    else:
                        print("History is empty.")

                elif event.key() == Qt.Key_Delete:
                    if self.galleryManager.isGalleryEmpty():
                        # TODO: set some generic image for background
                        print("Source directory is empty")
                        return

                    image_name = self.galleryManager.getCurrentFilename()
                    src = self.galleryManager.getSourcePath()
                    dst = src + "/" + "__DELETED__"
                    if not os.path.exists(dst):
                        os.makedirs(dst)
                    print(f"Nalezeno, lze presunout z {self.galleryManager.getSourcePath()} do {dst}!")

                    # Remove current image from the list of images in src directory
                    self.galleryManager.removeFile(image_name)
                    shutil.move(src + "/" + image_name, dst + "/" + image_name)
                    self.mv_history.append({"src": src, "dst": dst, "image": image_name, "gallery_index": self.galleryManager.getGalleryIndex()})
                    self.statusBarLabel.setText(f"File Deleted.")

                    # Update counter label
                    self.image_counter_label.setText(self.galleryManager.getCounterString())

                    # Show new image
                    self.galleryManager.updatePreview(self.previewLabel)

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

                        if self.galleryManager.isGalleryEmpty():
                            # TODO: set some generic image for background
                            print("Source directory is empty")
                            return

                        image_name = self.galleryManager.getCurrentFilename()
                        src = self.galleryManager.getSourcePath()
                        dst = self.shortcut_manager.get_dst_for_shortcut(full_shortcut)
                        print(f"Nalezeno, lze presunout z {self.galleryManager.getSourcePath()} do {dst}!")

                        # Remove current image from the list of images in src directory
                        if not self.copyOnly:
                            self.galleryManager.removeFile(image_name)
                            shutil.move(src + "/" + image_name, dst + "/" + image_name)
                            self.mv_history.append({"src": src, "dst": dst, "image": image_name, "gallery_index": self.galleryManager.getGalleryIndex()})
                            self.statusBarLabel.setText(f"File moved From: {src} to {dst}.")
                        else:
                            shutil.copy2(src + "/" + image_name, dst + "/" + image_name)
                            self.galleryManager.incrementGalleryIndex()
                            self.statusBarLabel.setText(f"File copied From: {src} to {dst}.")

                        # Update counter label
                        self.image_counter_label.setText(self.galleryManager.getCounterString())

                        # Show new image
                        self.galleryManager.updatePreview(self.previewLabel)

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


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

