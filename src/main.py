import sys
import json
from pathlib import Path
import shutil
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QTreeWidgetItem,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QShortcut,
    QMenu,
    QAction,
    QGraphicsDropShadowEffect, QSplitter,
)
from PyQt5.QtGui import QKeyEvent, QKeySequence, QCursor, QIcon

# pip3 install pyqt5
# pip3 install keyboard

from GalleryManager import GalleryManager
from ShortcutManager import ShortcutManager
from TreeItemWithButtons import TreeItemWithButtons
from CustomTreeWidget import CustomTreeWidget
from Styles import Styles

width = 1152
height = 864

# TODO: Translate DONE and TODO to EN:
# Features DONE:
# - [x] Pridat nekam, jaka src slozka je aktualne nastavena
# - [x] Pridat zobrazeni i 3. vnoreni zkratek
# - [x] Pridat counter (x/y), kolik obrazku zbyva v src slozce
# - [x] pridat kontrolu, ktere klavesy lze zmacknout (zablokovat napr. mezernik a bile znaky)
# - [x] Pridat Copy mode, aby se obrazek nepresunul, ale jen zkopiroval do dst.
# - [x] Delete current image (Presune se do slozky TO_DELETE, kde si to pak uzivatel bude moct rucne smazat - to aby porad fungovala funkce Undo - nevim, jak bych to dostaval z kose).
# - [x] Rozsirit Status bar na 2 radky.
# - [x] Pridat moznost zvolit file se shortcuts pro nacteni, a pri ukladani tez.
# - [x] Pridat, ze cudlik bude polopruhledny a po najeti se zviditelni.
# - [x] Pridat obrazky pro buttons (kos s cervenym backgroundem, a takoveto pero pro edit)
# - [x] Kdyz neni otevrena zadna src slozka, tak moct kliknout na plochu, kde byvaji obrazky, pro otevreni dialogu vyberu src slozky.
# - [x] Pridat filtr ze se nactou do galerie pouze .png, .jpeg, .jpg, .gif, proste jen obrazkove formaty. Zadna pdf a tak.
# - [x] Pridat obrazek do imagewidgetu, kdyz neni nactena zadna src slozka.
# - [x] Fixed: All Images were clickable instead of just the one when gallery is empty.
# - [x] Kdyz v galerii dojdou obrazky, vratit tam ten obrazek EmptyInbox.
# - [x] Track changes in shortcuts and ask for saving if changes were made.
# - [x] Pri nacteni shortcuts-dat ulozit cestu, odkud byla vzata a nabidnout ji pak kdyz chci ulozit zmeny.
# - [x] Po najeti na tlacitka/klikatelne veci, se zmeni kurzor na ruku.
# - [x] Zprovoznit ikonu aplikace
# - [x] FIX: searching longest path!
#
#
# Top priority:
# - [ ] Edit mode: Pridat moznost odstranit nejakou zkratku, podzkratku ... (o-a = 'o' 'minus' 'a') odstrani 'a' zkratku z rodicovske 'o'.
# - [ ] !!! Obrazek (label) by se mel zvetsit tak, aby zaplnil celou obrazovku, pokud zvetsim okno. Celkove resizing a responzivnost posefit.
# - [ ] !! Pridat cudliky na Jump to start of the gallery a na Jump to end of gallery. Dat je vedle Previous a Next image.
# - [ ] Fix focus, abych mohl pouzivat sipky pro prochazeni obrazku !!!
# - [ ] Next/Prev buttons, counter a src a image name se zobrazi jen, kdyz je nactena galerie.
#
# Features TODO:
# - [~] ! REFACTORING
# - [~] Pridat moznost zobrazovat i gify (movie widget misto imageWidgetu)
# - [~] Pridat testy (make test)
# - [ ] SORT mode: mit moznost normalne klikat na ta jednotliva pole ve strome, a tam se pri kliknuti obrazek presune.
# - [ ] MAYBE: Pridat AI advices based on keywords on image.
# - [ ] Zobrazit historii v History Label kde bude historie zmacknutych zkratek ('afg', ...), aby clovek videl, co se stane, kdyz zmackne '.' (Repeat).
# - [ ] Zobrazit nazev nactenych dat (soubor se zkratkama).
# - [ ] Edit/Delete buttons v Tree se zobrazi pouze v Edit modu.
# - [ ] Nad Nazvama sloupcu by mohl byt label, kde bude zobrazen nazev nacteneho souboru se shortcuts-daty.
# - [ ] Deriv subclass of treeitem kterej bude obsahovat cudly na remove a edit a dalsi specialni obsahujici pouze cudl Add naspod kazde kategorie a podkategorie.
# - [ ] udelat ikonu pro aplikaci: ikonka obrazek a na ni dat "axc" (Neco jako tam je ted, ale dopsat napis??)
# - [ ] Udelat CustomTree resizable pomoci QSplitter
# - [ ] CustomTreeWidget: 1. Jak zvolit, kolik ma zobrazit sloupcu?? 2. Jak prizpusobit sirku - na zaklade poctu zobrazenych sloupcu?
#
# Design:
# - [~] Udelat nejakou stylovaci tridu, kde pujde menit treba shadow offset na jednom miste pro vse...
#
# To Fix:
# - [ ] Crashing when moving the .git bcz process (medium) is used or what...
#
# Shortcuts management:
# - [~] Klikatko pro pridani a odstraneni zkratky / podzkratky
# - [ ] Po najeti na zkracenou cestu (napr. Images, Naruto, ...) se okamzite zobrazi cela cesta (v bubline).
# - [ ] Pridat zvyraznovani aktualne namacknute zkratky a filtraci - zustane pouze ta a jeji podzkratky.
# - [ ] Pridat nekam indikator, jestli jsou provedeny zmeny, nebo ne. (Obvykle je nekde treba '*').
#
# Minor issues:
# - [ ] Prepsat vse z CZ do EN
# - [ ] Stabni kultura - vse prepsat z var_xyz() na varXyz()
# - [ ] Pridat radu do helpu: Namapovat co nejvic zkratek pod prsty leve ruky (a, e, d, ...)
# - [ ] Pridat radu do helpu: Udelat si mensi shortcuts pro konkretni slozky jako Gaming, a pod.
# - [ ] Separatni repozitar, hodit na reddit, na RH, kolegum,
# - [ ] Pridat slovo "EMPTY" do Inbox obrazku
#
# TODO: Promyslet:
# - Kdyz mam oi, kde je 'n', tak se bud provede vzdy az 'n', nebo pouze oi. Jak to udelat, aby bylo an vyber? Bude takova moznost?
# ze jakmile vytvorim podslozku, tak uz nepujde nic priradit do rodicovske slozky teto slozky? Jakoze, kdyz budu mit slozku Naruto ve slozce Anime, tak
# uz nic nepujde dat do Anime, ale pouze do dalsi podslozky? Pripadne, pridat moznost do configu nastavit casovy interval, po ktery pujde stisknout dodatecna klavesa, jinak se to presune do 'oa' ?
# NEBO:
# zadny interval, ale proste pri sub-sequenci, treba to 'oi', se stejne ceka na dalsi key, pokud obsahuje 'oi' dalsi subkeys, tak proste muzu dat enter, a ono se to tam presune. Takovej "Force" move.

allowed_keys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
                Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
                Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z]


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Keysort")
        self.setWindowIcon(QIcon(':Resources/icon.jpg'))
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        self.setStyleSheet("""
            QWidget {
                font-family: "Inter";
            }
        """)

        # Management objects
        self.shortcut_manager = ShortcutManager(self)
        self.galleryManager = GalleryManager(self)
        self.galleryManager.setStyleSheet(f"""
            __width: 150px;
            border: 1px solid black;
            border-radius: {Styles.widgetBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
        """)

        main_layout = QHBoxLayout()
        left_inner_layout = QVBoxLayout()
        right_inner_layout = QVBoxLayout()

        main_window_widget = QWidget()
        main_window_widget.setLayout(main_layout)
        main_window_widget.setFocus(True)
        # main_window_widget.setStyleSheet("background-color: rgb(200, 200, 200);")
        self.setCentralWidget(main_window_widget)

        # Add sub-layouts into the main layout
        main_layout.addLayout(left_inner_layout)
        main_layout.addLayout(right_inner_layout)

        self.source_dir_label = QLabel("Not selected")
        self.source_dir_label.setMaximumHeight(30)
        self.source_dir_label.setStyleSheet(f"""
            QLabel {{
                min-height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                background-color: {Styles.widgetsBgColor};
                font-weight: bold;
                font-size: 15px;
                xxmargin: 5px;
                }}
            """)
        right_inner_layout.addWidget(self.source_dir_label)

        self.image_filename_label = QLabel()
        self.image_filename_label.setMaximumHeight(30)
        self.image_filename_label.setStyleSheet(f"""
            QLabel {{
                _min-height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                background-color: {Styles.widgetsBgColor};
                font-weight: bold;
                font-size: 15px;
                xxmargin: 5px;
                }}
            """)
        # self.image_filename_label.setStyleSheet("background-color: green; border: 1px solid black; padding: 1px;")
        right_inner_layout.addWidget(self.image_filename_label)

        # Right side of the main layout
        right_inner_layout.addWidget(self.galleryManager)

        previousshadowEffect = QGraphicsDropShadowEffect()
        previousshadowEffect.setOffset(3, 3)
        previousshadowEffect.setBlurRadius(10)
        self.previous_image_button = QPushButton("&Previous", self)
        self.previous_image_button.clicked.connect(self.showPreviousImage)
        self.previous_image_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.previous_image_button.setFocus(True)
        self.previous_image_button.setGraphicsEffect(previousshadowEffect)
        self.previous_image_button.setStyleSheet(f"""
        QPushButton {{
            width: 150px;
            height: 20px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
            font-weight: bold;
            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: {Styles.buttonHoverBgColor};
        }}
        """)

        nextshadowEffect = QGraphicsDropShadowEffect()
        nextshadowEffect.setOffset(3, 3)
        nextshadowEffect.setBlurRadius(10)
        self.next_image_button = QPushButton("&Next", self)
        self.next_image_button.clicked.connect(self.showNextImage)
        self.next_image_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.next_image_button.setFocus(True)
        self.next_image_button.setGraphicsEffect(nextshadowEffect)
        self.next_image_button.setStyleSheet(f"""
        QPushButton {{
            width: 150px;
            height: 20px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
            font-weight: bold;
            font-size: 15px;

        }}
        QPushButton:hover {{
            background-color: {Styles.buttonHoverBgColor};
        }}
        """)

        self.image_counter_label = QLabel()
        self.image_counter_label.setStyleSheet("font-size: 20px;")
        self.image_counter_label.setText("0/0")

        right_control_buttons_layout = QHBoxLayout()
        right_control_buttons_layout.addWidget(self.previous_image_button)
        right_control_buttons_layout.addStretch()
        right_control_buttons_layout.addWidget(self.image_counter_label)
        right_control_buttons_layout.addStretch()
        right_control_buttons_layout.addWidget(self.next_image_button)

        right_inner_layout.addLayout(right_control_buttons_layout)

        statusshadowEffect = QGraphicsDropShadowEffect()
        statusshadowEffect.setOffset(3, 3)
        statusshadowEffect.setBlurRadius(10)
        self.statusBarLabel = QLabel("Status bar")
        self.statusBarLabel.setGraphicsEffect(statusshadowEffect)
        self.statusBarLabel.setMaximumHeight(25)
        # self.statusBarLabel.setStyleSheet("""
        #     border: 1px solid black;
        #     border-radius: 5px;
        # """)
        self.statusBarLabel.setStyleSheet(f"""
            QLabel {{
                min-height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                background-color: {Styles.widgetsBgColor};
                font-weight: bold;
                font-size: 15px;
                xxmargin: 5px;
                }}
            """)
        self.statusBarLabel.setWordWrap(True)
        right_inner_layout.addWidget(self.statusBarLabel)

        # Left side of the main layout
        key_labelshadowEffect = QGraphicsDropShadowEffect()
        key_labelshadowEffect.setOffset(3, 3)
        key_labelshadowEffect.setBlurRadius(10)
        self.key_label = QLabel("Key Sequence Pressed: \nNone")
        self.key_label.resize(self.key_label.sizeHint())
        self.key_label.setGraphicsEffect(key_labelshadowEffect)
        self.key_label.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            height: 20px;
            border: 1px solid black;
            border-radius: {Styles.widgetBorderRadius}px;
            color: rgb(171, 110, 3);
            background-color: {Styles.widgetsBgColor};
            """)
        self.key_label.setAlignment(Qt.AlignCenter)

        copy_buttonshadowEffect = QGraphicsDropShadowEffect()
        copy_buttonshadowEffect.setOffset(3, 3)
        copy_buttonshadowEffect.setBlurRadius(10)
        self.copy_button = QPushButton("&Copy", self)
        self.copy_button.clicked.connect(self.toggleCopyMode)
        self.copy_button.setGraphicsEffect(copy_buttonshadowEffect)
        self.copy_button.setToolTip("Toggle copy mode (switch between copy and move operation).")
        self.copy_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.copy_button.setStyleSheet(f"""
        QPushButton {{
            width: 150px;
            height: 20px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
            font-weight: bold;
            font-size: 15px;
        }}
        _QPushButton:hover {{
            background-color: {Styles.buttonHoverBgColor};
        }}
        """)

        edit_buttonshadowEffect = QGraphicsDropShadowEffect()
        edit_buttonshadowEffect.setOffset(3, 3)
        edit_buttonshadowEffect.setBlurRadius(10)
        self.edit_button = QPushButton("&Edit", self)
        self.edit_button.clicked.connect(self.set_edit_mode)
        self.edit_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.edit_button.setGraphicsEffect(edit_buttonshadowEffect)
        self.edit_button.setStyleSheet(f"""
        QPushButton {{
            width: 150px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
            font-weight: bold;
            font-size: 15px;
        }}
        _QPushButton:hover {{
            background-color: {Styles.buttonHoverBgColor};
        }}
        """)

        sort_buttonshadowEffect = QGraphicsDropShadowEffect()
        sort_buttonshadowEffect.setOffset(3, 3)
        sort_buttonshadowEffect.setBlurRadius(10)
        self.sort_button = QPushButton("&Sort", self)
        self.sort_button.clicked.connect(self.set_sort_mode)
        self.sort_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.sort_button.setGraphicsEffect(sort_buttonshadowEffect)
        self.sort_button.setStyleSheet(f"""
        QPushButton {{
            __width: 150px;
            border: 1px solid black;
            border-radius: {Styles.buttonBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
            font-weight: bold;
            font-size: 15px;
        }}
        QPushButton:hover {{
            background-color: {Styles.buttonHoverBgColor};
        }}
        """)
        # self.sort_button.setStyleSheet(Styles.getButtonStyles())

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
        self.current_mode = "home"  # Next options: edit, sort
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
        self.tree = CustomTreeWidget()
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                border: 1px solid black;
                border-radius: 10px;
                background-color: {Styles.widgetsBgColor};
                __padding: 2px;
            }}
            
            QTreeWidget::header {{
                background-color: red;
                min-height: 30px;
            }}
            
            QHeaderView {{
                background-color: {Styles.widgetsBgColor};
                color: black;
                border: 0px solid black;
                border-radius: 10px;
                margin-top: 8px;
                min-height: 30px;
            }}
            
            QHeaderView::section {{
                _color: green;
                font-weight: bold;
                background-color: rgb(214, 137, 60);
                _border: 1px solid black;
                _border-radius: 10px;
                padding: 3px;
                
                _margin: 3px;
                _min-height: 20px;
            }}
        """)
        treeshadowEffect = QGraphicsDropShadowEffect()
        treeshadowEffect.setOffset(3, 3)
        treeshadowEffect.setBlurRadius(10)
        self.tree.setGraphicsEffect(treeshadowEffect)
        self.tree.setMaximumWidth(250)
        left_inner_layout.addWidget(self.tree)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Shortcut", "Directory", "Actions"])
        self.tree.setColumnWidth(0, 90)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 50)
        # self.tree.setEnabled(False)
        self.update_tree_view()

        # Update Counter label
        self.image_counter_label.setText(self.galleryManager.getCounterString())

        # Create main Menu bar
        self._createActions()
        self._createMenuBar()
        self._connectActions()

        self.galleryManager.emptyInboxWidget.selectSourceSignal.connect(self.galleryManager.selectSourceDirectory)
        # self.galleryManager.updatePreview()

        # vvvvvvvv TODO: Remove. [Just for DEBUG]: Manually setting src dir
        # self.galleryManager.setSourcePath("/home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/test/downloads")
        # self.galleryManager.setSourcePath(r"C:\Users\Kyuubi\Repositories\WorkstationSetup\scripts\image-sorter\test\downloads")
        # self.source_dir_label.setText(f"Source directory: {self.galleryManager.getSourcePath()}")
        # ^^^^^^^^^

        # Sort mode is default mode when app starts
        self.set_sort_mode()

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
        if self.shortcut_manager.areShortcutsModified():
            self.shortcut_manager.save_shortcuts()

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
        self.galleryManager.setNextImage()
        self.image_counter_label.setText(self.galleryManager.getCounterString())

    def showPreviousImage(self):
        self.galleryManager.setPreviousImage()
        self.image_counter_label.setText(self.galleryManager.getCounterString())

    # TODO: Telo presunout do CustromTreeWidget a sem pridat pouze volani teze funkce v customtreewidgetu.
    def update_tree_view(self):
        # Just flush the whole content of the tree and rebuild it from scratch.
        self.tree.clear()
        items = []
        shortcuts_data = self.shortcut_manager.get_data()

        for key_L1, values_L1 in shortcuts_data["keys"].items():
            # print("Key a value", key, values)
            dst_path_L1 = values_L1["dst_path"]
            item_L1 = QTreeWidgetItem([key_L1, Path(dst_path_L1).name])
            # self.tree.expandItem(item)
            for key_L2, values_L2 in values_L1["keys"].items():
                dst_path_L2 = values_L2["dst_path"]
                item_L2 = QTreeWidgetItem([key_L2, Path(dst_path_L2).name])
                for key_L3, values_L3 in values_L2["keys"].items():
                    item_L3 = QTreeWidgetItem([key_L3])
                    dst_path_L3 = values_L3["dst_path"]
                    child = QTreeWidgetItem([key_L3, Path(dst_path_L3).name])
                    item_L2.addChild(child)
                    print(f"DBD: L3 val: {values_L3}")
                item_L1.addChild(item_L2)
            items.append(item_L1)

        newItem = QTreeWidgetItem(["test"])
        items.append(newItem)

        self.tree.insertTopLevelItems(0, items)

        myWidget = TreeItemWithButtons()
        self.tree.setItemWidget(newItem, 2, myWidget)

        self.tree.expandAll()


    def save_data(self):
        self.shortcut_manager.save_shortcuts()

    def load_data(self):
        if not self.shortcut_manager.load_shortcuts():
            return
        self.update_tree_view()

    def undo_last_operation(self):
        print("Undo last operation")
        # print(self.mv_history)

        if not self.mv_history:
            print(f"History is Empty!")
            return

        image_name = self.mv_history[-1]["image"]
        src = self.mv_history[-1]["dst"]
        dst = self.mv_history[-1]["src"]
        positionIndex = self.mv_history[-1]["gallery_index"]

        if not os.path.exists(dst):
            print(f"ERROR: Destination directory {dst} does not exist.")
            return

        shutil.move(src + "/" + image_name, dst + "/" + image_name)
        self.statusBarLabel.setText(f"File moved BACK From: {src}.")

        # Remove current image from the list of images in src directory
        self.galleryManager.addFile(image_name, positionIndex)

        # Update counter label
        self.image_counter_label.setText(self.galleryManager.getCounterString())

        # Remove last record from history
        if self.mv_history:
            self.mv_history.pop()

        # Show new image
        self.galleryManager.updatePreview()
        # print(self.images)

    def toggleCopyMode(self):
        self.next_image_button.setFocus()
        if self.copyOnly is False:
            print("Current mode: Copy")
            self.copyOnly = True
            self.copy_button.setStyleSheet(f"""
            QPushButton {{
                width: 150px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonActivatedBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            _QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
            """)
            return

        if self.copyOnly is True:
            print("Current mode: Move")
            self.copyOnly = False
            self.copy_button.setStyleSheet(f"""
            QPushButton {{
                width: 150px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            _QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
            """)
            return

    def set_edit_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Edit")
        self.current_mode = "edit"
        self.edit_button.setStyleSheet(f"""
            QPushButton {{
                __width: 100px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonActivatedBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
            """)
        self.sort_button.setStyleSheet(f"""
            QPushButton {{
                __width: 100px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
            """)
        self.tree.setColumnHidden(2, False)
        self.tree.setEnabled(True)

    def set_sort_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Sort")
        self.current_mode = "sort"
        self.edit_button.setStyleSheet(f"""
            QPushButton {{
                __width: 150px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
            """)
        self.sort_button.setStyleSheet(f"""
            QPushButton {{
                __width: 150px;
                height: 20px;
                border: 1px solid black;
                border-radius: {Styles.buttonBorderRadius}px;
                padding: 3px;
                background-color: {Styles.buttonActivatedBgColor};
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {Styles.buttonHoverBgColor};
            }}
            """)
        self.tree.setColumnHidden(2, True)
        self.tree.setEnabled(False)

    # TODO: Rozbit na mensi kousky:
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
                super().keyPressEvent(event)

            # TODO: Refactor following if-else hell:  !!!!!!!!!!!!!
            # ==== EDIT MODE ====
            if self.current_mode == "edit":
                if event.key() == Qt.Key_Escape:
                    self.key_seq_history.append(self.key_seq)
                    self.key_seq = ""
                    self.updateKeySequenceLabel()

                # Confirm entered shortcut
                elif event.key() == Qt.Key_Return:  # "Return" is the "Enter" key in the center of keyboard.
                    if not self.key_seq:
                        print("probably empty")
                        return

                    # Check, whether sequence contains '-', and if so
                    # consider this as removing all shortcuts after the '-' character.
                    if "-" in self.key_seq:
                        # TODO
                        # self.shortcut_manager.removeShortcutSequence(self.key_seq)
                        # Jak? Projit od zacatku stringu, jak narazim na -, tak od te doby smazat nasledujici podstrom,
                        # pokud existuje.
                        # for key in self.key_seq:
                        #   if key == "-":
                        #       ...
                        self.key_seq = ""
                        return

                    # Add new shortcut sequence
                    for k in self.key_seq:
                        self.shortcut_manager.add_shortcut(self.key_seq)
                        # if k == self.key_seq[-1]:
                    dst_sort_directory = QFileDialog.getExistingDirectory(self, "Select Directory")
                    self.shortcut_manager.add_dst_path(self.key_seq, dst_sort_directory)
                    self.key_seq = ""
                    self.updateKeySequenceLabel()
                    self.update_tree_view()
                    print(json.dumps(self.shortcut_manager.get_data(), indent=2))

                else:
                    self.key_seq += pressed_key
                    self.updateKeySequenceLabel()

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
                    self.updateKeySequenceLabel()

                # Hold current shortcut and use it as default for upcoming sequences until escape
                elif event.key() == Qt.Key_Return:  # Key_Return is non-numeric Enter key
                    print("ENTER")

                    if self.key_seq:
                        self.permanent_key_seq = self.key_seq
                        self.key_seq = ""

                    self.updateKeySequenceLabel()

                # Repeat last move from src to dst of current image.
                elif event.key() == Qt.Key_Period:
                    print("Repeat last finished command for current image")

                    if len(self.mv_history) <= 0 or len(self.key_seq_history) <= 0:
                        print("History is empty.")
                        return

                    print(f"Last history entry: {self.key_seq_history[-1]}")

                    image_name = self.galleryManager.getCurrentFilename()

                    src = self.mv_history[-1]["src"]
                    dst = self.mv_history[-1]["dst"]

                    if not os.path.exists(dst):
                        print(f"ERROR: Destination directory {dst} does not exist.")
                        return

                    # Remove current image from the list of images in src directory
                    if not self.copyOnly:
                        self.galleryManager.removeFile(image_name)
                        shutil.move(src + "/" + image_name, dst + "/" + image_name)
                        self.mv_history.append({"src": src, "dst": dst, "image": image_name, "gallery_index": self.galleryManager.getGalleryIndex()})
                        self.statusBarLabel.setText(f"File moved to {dst}.")
                    else:
                        shutil.copy2(src + "/" + image_name, dst + "/" + image_name)
                        self.galleryManager.incrementGalleryIndex()
                        self.statusBarLabel.setText(f"File copied to {dst}.")

                    # Update counter label
                    self.image_counter_label.setText(self.galleryManager.getCounterString())

                    # Show new image
                    self.galleryManager.updatePreview()


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
                    self.galleryManager.updatePreview()

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

                    # print("dst for shortcut:", self.shortcut_manager.get_dst_for_shortcut(full_shortcut))
                    if not self.key_seq:
                        return

                    if self.shortcut_manager.get_dst_for_shortcut(full_shortcut):
                        print("HIT!")

                        if self.galleryManager.isGalleryEmpty():
                            print("Source directory is empty")
                            self.key_seq = ""
                            self.updateKeySequenceLabel()
                            return

                        image_name = self.galleryManager.getCurrentFilename()
                        src = self.galleryManager.getSourcePath()
                        dst = self.shortcut_manager.get_dst_for_shortcut(full_shortcut)

                        if not os.path.exists(dst):
                            print(f"ERROR: Destination directory {dst} does not exist.")
                            return

                        self.key_seq_history.append(full_shortcut)

                        print(f"Nalezeno, lze presunout z {self.galleryManager.getSourcePath()} do {dst}!")

                        # Remove current image from the list of images in src directory
                        if not self.copyOnly:
                            self.galleryManager.removeFile(image_name)
                            shutil.move(src + "/" + image_name, dst + "/" + image_name)
                            self.mv_history.append({"src": src, "dst": dst, "image": image_name, "gallery_index": self.galleryManager.getGalleryIndex()})
                            self.statusBarLabel.setText(f"File moved to {dst}.")
                        else:
                            shutil.copy2(src + "/" + image_name, dst + "/" + image_name)
                            self.galleryManager.incrementGalleryIndex()
                            self.statusBarLabel.setText(f"File copied to {dst}.")

                        # Update counter label
                        self.image_counter_label.setText(self.galleryManager.getCounterString())

                        # Show new image
                        self.galleryManager.updatePreview()

                        # Enable temporaly save and reuse partial shortcut
                        self.key_seq = ""
                        self.updateKeySequenceLabel()
                    else:
                        self.updateKeySequenceLabel()
            else:
                pass

    def updateKeySequenceLabel(self):
        separator = "+"
        if self.permanent_key_seq:
            self.key_label.setText(f"Key Sequence Pressed: \n{self.permanent_key_seq}{separator}{self.key_seq}")
        else:
            self.key_label.setText(f"Key Sequence Pressed: \n{self.key_seq}")

    def updateStatusBarLabel(self, src, dst):
        self.statusBarLabel.setText(f"File copied to {dst}.")

    def parse_sequence(self):
        pass

    def dispatcher(self, key_pressed):
        # if hit() then move image from src to dst. and save sequence into history.
        pass


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(f"""
        QWidget {{
            background-color: {Styles.mainBackground};
        }}
    """)
    window = MainWindow()
    window.show()
    app.aboutToQuit.connect(window.shortcut_manager.askSaveIfChanged)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

