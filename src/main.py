import sys
import json
from pathlib import Path
import shutil
import os
import webbrowser

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
    QGraphicsDropShadowEffect,
    QSplitter,
    QProgressBar,
    QTreeWidget
)
from PyQt5.QtGui import QKeyEvent, QKeySequence, QCursor, QIcon

# pip3 install pyqt5
# pip3 install keyboard

from src.GalleryManager import GalleryManager
from src.ShortcutManager import ShortcutManager
from src.TreeItemWithButtons import TreeItemWithButtons
from src.CustomTreeWidget import CustomTreeWidget
from src.Styles import Styles

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
# - [x] Next/Prev buttons, counter a src a image name se zobrazi jen, kdyz je nactena galerie.
# - [x] Edit mode: Pridat moznost odstranit nejakou zkratku, podzkratku ... (o-a = 'o' 'minus' 'a') odstrani zkratku 'a' z rodicovske 'o'.
# - [x] Prerusit to vetveni x.y.z.f() mezi main.GalleryManager.MediaContainerWidget.f() [Jak to delat lepe, nez ze udelat retezec funkci?]
# - [x] Fix focus, abych mohl pouzivat sipky pro prochazeni obrazku.
# - [x] Pridat cudliky na Jump to start of the gallery a na Jump to end of gallery. Dat je vedle Previous a Next image.
# - [x] Add error message, if the directory does not exist, for which we HIT the shortcut (is in shortcut, but does nto exist on disk)
# - [x] Fix: HIT is detected even for sequences containing intermediate nonexisting keys: fxxxxk, oxa, ...
# - [x] Empty the shortcuts (or just update the preview?) if HIT && target dir does not exist physically.
# - [x] Resize image in label to fill the label while keeping ratio and even during the window resizing.
# - [x~] Pridat nekam indikator, jestli jsou provedeny zmeny, nebo ne. (Obvykle je nekde treba '*').
# - [x] Fix crash, when manipulating image, which is removed outside of program, while source directory is loaded.
#   - Kontext: Odstranim/presunu rucne obrazek ve slozce, ktera je otevrena v programu. Kdyz na obrazek (ktery v poli ale porad existuje) sipkama dojdu a zkusim ho odstranit, program crashne.
#   - [x] Pridat file exist check pri manipulaci s obrazkem (pri mv, copy, del) !!!! If does not exist, remove from list.
# - [x] CHECK: co kdyz presunu do dst picture s nazvem Xyz, ale obrazek s timto nazvem jiz ve slozce je? Neprepise se doufam...
# - [x] Pridat klavesovou zkratku pro Na konec a Na zacatek - home a end klavesy.
# - [x] VideoWidget: spravit avi, zprovoznit mp4, nextImage stopne video if current is video, prev to same.
# - [x] Pridat moznost zobrazovat i gify (videoWidget misto imageWidgetu)
# - [x] ! Zmenit border color okna s obrazkama, kdyz je aktivni COPY mode, aby to bylo jasnejsi (uz jsem na nej parkrat zapomenul, ze je aktivni).
# - [x] Vyresit cekani na zkratku, kdyz x, aj xy obsahuje cestu. Kdyz chci poslat img do 'x', nic se nedeje, bo y obsahuje cestu taky. Mozna Timer nebo treba >>>mezernik<<< jako potvrzeni. !!!!!!
# - [x] zmacknutim mezerniku (if Sort mode AND pokud neni namacknuta zadna zkratka), otevre okno s vyberem slozky, kam jednorazove poslat aktualni obrazek.
#
#
# Top priority:
# - [ ] !!! Pridat CLI argumenty pro spusteni aplikace s preddefinovanymi parametry (napr. --src-dir, --dst-dir, --load-data, --save-data, ...)
# - [ ] !!!! Otestovat cisla a velka pismena jako shortcuts !!!!!!!!
# - [ ] MOZNA: Pridat i nektere znaky jako labely ($, ...)
# - [ ] Vypisuji se jen 3 urovne zkratek. Oznacit ale nejak, ze (a pokud) tam je dalsi uroven, (proto sekvence treba neHITla, bo se tam skryvaly dalsi). [SETTINGS]
# - [ ] Prochazet TODO v souborech a udelat je.
# - [~] ! Napsat unit testy !!
#
#
# Settings:
# - [ ] How many columns of shortcuts to show (1-5)
# - [ ] ! Pridat Settings - kde pujde zaskrtnout, jestli povolit pridavani zkratek bez vybrane cesty. !!! To je napad!
# - [ ] Settings saving and loading.
# - [ ] Settings - na jake misto soubor hodit? Kam se divat defaultne? Win vs Linux (~/).
# - [ ] Settings - ovladani hlasitosti - mute by default???
#
#
# Important features TODO:
# - [~] ! REFACTORING
# - [ ] Tridit zkratky abecedne? (Mozna settings option?)
# - [ ] ! Fix reskalovani toho Shortuc panelu - obcas se zmensuje a zvetsuje dle zobrazeneho obrazku.
# - [ ] ! FIX: Kdyz se pri tvorbe nove zkratky nevybere zadna cesta, tak zkratku nepridavat.! Aktualne se prida prazdna. Nebo dialog okno esi fakt pridat. [??SETTINGS]
# - [ ] Zobrazit historii v History Label kde bude historie zmacknutych zkratek ('afg', ...), aby clovek videl, co se stane, kdyz zmackne '.' (Repeat). Mozna ji pridat POD aktualne mackanou zkratku, sedou barvou.
# - [ ] Zobrazit nazev nactenych dat (soubor se zkratkama) (Nad Nazvama sloupcu by mohl byt label, kde bude zobrazen nazev nacteneho souboru se shortcuts-daty.)
# - [ ] ! Pridat varovani, kdyz uz zkratka existuje, a my ji chceme prepsat dst path. (Vyskoci dialog okno ze uz existuje, jestli ji chceme prepsat.)
# - [ ] Moznost prejmenovat obrazek - udelat textfield z labelu pro imagename.
# - [ ] Moznost napsat, na kolikaty obrazek se chceme presunout - udelat textfield z image counter labelu.
# - [ ] Pridat moznost pouzivat backspace, abych mohl odmazat znak ze psane zkratky??
# - [ ] ! Kdyz pridavam zkratku pod nejakou jinou, nabidnout primarne cestu teto vyssi zkratky, nebo zkratky paralelne k teto, pokud takova existuje.
#
#
# Design:
# - [~] Udelat nejakou stylovaci tridu, kde pujde menit treba shadow offset na jednom miste pro vse...
#
# To Fix:
# - [x] Crashing when moving the .git bcz process (medium) is used or what...
# - [ ] ??! Fix error state: 1.) add 'hd' without chosing path. 2.) remove 'd': 'h-d'. 3.) add 'hd'. 4.) issue - empty shortcut on L1 .....CANNOT REPRODUCE NOW.....
#   
#
# Shortcuts management, Shortcut Tree (GUI):
# - [ ] Shortcuts by mely byt scrollovatelne i v Sort modu!
# - [ ] Sort shortcuts alphabetically (a, A, c, G, x) and option2 sort target directories alphabetically.
# - [ ] CustomTreeWidget: 1. Jak zvolit, kolik ma zobrazit sloupcu?? 2. Jak prizpusobit sirku - na zaklade poctu zobrazenych sloupcu? [SETTINGS]
# - [~] Edit/Delete buttons v Tree se zobrazi pouze v Edit modu.
# - [ ] Deriv subclass of treeitem kterej bude obsahovat cudly na remove a edit a dalsi specialni obsahujici pouze cudl Add naspod kazde kategorie a podkategorie.
# - [ ] Udelat CustomTree resizable pomoci QSplitter
# - [~] Klikatko pro pridani a odstraneni zkratky / podzkratky
# - [ ] Po najeti na zkracenou cestu (napr. Images, Naruto, ...) se okamzite zobrazi cela cesta (v bubline).
# - [ ] SORT mode: mit moznost normalne klikat na ta jednotliva pole ve strome, a tam se pri kliknuti obrazek presune.
# - [ ] Pridat zvyraznovani aktualne namacknute zkratky a filtraci - zustane pouze ta a jeji podzkratky.
# - [ ] Pod posledni prvek kazde sekce udelat tenkou caru jako oddelovac. (Nebo nad kazdou hlavni, bo to je root tak by to bylo jednodussi).
# - [ ] Pridat moznost otevrit slozku pri kliknuti na shortcut (Tohle funguje!!!):
#           webbrowser.open(self.shortcutManager.srcPathOfLoadedData)
#
#
# Minor issues, future features:
# - [ ] Stabni kultura - vse prepsat z var_xyz() na varXyz()
# - [ ] Pridat radu do helpu: Namapovat co nejvic zkratek pod prsty leve ruky (a, e, d, ...)
# - [ ] Pridat radu do helpu: Udelat si mensi shortcuts pro konkretni slozky jako Gaming, a pod.
# - [ ] Vyresit ? pomale nacitani velkych obrazku (6MB+)
# - [ ] Separatni repozitar, hodit na reddit, na RH, kolegum,
# - [ ] Pridat slovo "EMPTY" do Inbox obrazku
# - [ ] udelat ikonu pro aplikaci: ikonka obrazek a na ni dat "axc" (Neco jako tam je ted, ale dopsat napis??)
# - [~] Dodelat progress widget
# - [ ] MAYBE: Pridat AI advices based on keywords on image.
# - [ ] Po dotrideni inboxu zobrazit tabulku s gratulaci, treba poctem setridenych obrazku, mozna animace famfar.
#

allowedKeys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
                Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
                Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z]


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.appTitle = "Image Keysort"
        self.setWindowTitle(self.appTitle)
        self.setWindowIcon(QIcon(':Resources/icon.jpg'))
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)
        self.setStyleSheet("""
            QWidget {
                font-family: "Inter";
            }
        """)

        # Management objects
        self.shortcutManager = ShortcutManager(self)
        self.galleryManager = GalleryManager(self)
        self.galleryManager.setStyleSheet(f"""
            __width: 150px;
            border: 1px solid black;
            border-radius: {Styles.widgetBorderRadius}px;
            padding: 3px;
            background-color: {Styles.widgetsBgColor};
        """)

        mainLayout = QHBoxLayout()
        leftInnerLayout = QVBoxLayout()
        rightInnerLayout = QVBoxLayout()

        mainWindowWidget = QWidget()
        mainWindowWidget.setLayout(mainLayout)
        mainWindowWidget.setFocus(True)
        self.setCentralWidget(mainWindowWidget)

        # Add sub-layouts into the main layout
        mainLayout.addLayout(leftInnerLayout)
        mainLayout.addLayout(rightInnerLayout)

        # Right side of the main layout
        rightInnerLayout.addWidget(self.galleryManager)

        self.statusBarLabel = QLabel("Status bar")
        self.statusBarLabel.setGraphicsEffect(Styles.getShadowEffect())
        self.statusBarLabel.setMaximumHeight(25)
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
        rightInnerLayout.addWidget(self.statusBarLabel)

        # Left side of the main layout
        self.keyLabel = QLabel("Key Sequence Pressed: \nNone")
        self.keyLabel.resize(self.keyLabel.sizeHint())
        self.keyLabel.setGraphicsEffect(Styles.getShadowEffect())
        self.keyLabel.setStyleSheet(f"""
            font-size: 16px;
            font-weight: bold;
            height: 20px;
            border: 1px solid black;
            border-radius: {Styles.widgetBorderRadius}px;
            color: rgb(171, 110, 3);
            background-color: {Styles.widgetsBgColor};
            """)
        self.keyLabel.setAlignment(Qt.AlignCenter)

        self.expProgress = QProgressBar()
        self.expProgress.setStyleSheet(f"""
            max-width: 250px;
        """)
        self.expProgress.setValue(20)

        self.copyButton = QPushButton("&Copy", self)
        self.copyButton.clicked.connect(self.toggleCopyMode)
        self.copyButton.setFocusPolicy(Qt.NoFocus)
        self.copyButton.setGraphicsEffect(Styles.getShadowEffect())
        self.copyButton.setToolTip("Toggle copy mode (switch between copy and move operation).")
        self.copyButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.copyButton.setStyleSheet(f"""
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

        self.editButton = QPushButton("&Edit", self)
        self.editButton.clicked.connect(self.set_edit_mode)
        self.editButton.setFocusPolicy(Qt.NoFocus)
        self.editButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.editButton.setGraphicsEffect(Styles.getShadowEffect())
        self.editButton.setStyleSheet(f"""
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


        self.sortButton = QPushButton("&Sort", self)
        self.sortButton.clicked.connect(self.set_sort_mode)
        self.sortButton.setFocusPolicy(Qt.NoFocus)
        self.sortButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.sortButton.setGraphicsEffect(Styles.getShadowEffect())
        self.sortButton.setStyleSheet(f"""
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

        leftInnerButtonLayout = QHBoxLayout()
        leftInnerButtonLayout.addWidget(self.editButton)
        leftInnerButtonLayout.addWidget(self.sortButton)

        leftInnerLayout.addWidget(self.expProgress)
        leftInnerLayout.addWidget(self.copyButton)
        leftInnerLayout.addLayout(leftInnerButtonLayout)
        leftInnerLayout.addWidget(self.keyLabel)

        # vars for history entries
        self.keySeqHistory = []
        self.mvHistory = []
        self.keySeq = ""
        self.permanentKeySeq = ""
        self.currentMode = "home"  # Next options: edit, sort
        self.copyOnly = False
        print("Mod: " + self.currentMode)

        # Register global keyboard shortcuts:
        setEditModeSeq = QKeySequence(Qt.CTRL + Qt.Key_E)
        self.setEditModeShortcut = QShortcut(setEditModeSeq, self)
        self.setEditModeShortcut.activated.connect(self.set_edit_mode)

        setSortModeSeq = QKeySequence(Qt.CTRL + Qt.Key_R)
        self.setSortModeShortcut = QShortcut(setSortModeSeq, self)
        self.setSortModeShortcut.activated.connect(self.set_sort_mode)

        undoSeq = QKeySequence(Qt.CTRL + Qt.Key_Z)
        self.undoShortcut = QShortcut(undoSeq, self)
        self.undoShortcut.activated.connect(self.undo_last_operation)

        saveDataSeq = QKeySequence(Qt.CTRL + Qt.Key_S)
        self.saveDataShortcut = QShortcut(saveDataSeq, self)
        self.saveDataShortcut.activated.connect(self.save_data)

        loadDataSeq = QKeySequence(Qt.CTRL + Qt.Key_L)
        self.loadDataShortcut = QShortcut(loadDataSeq, self)
        self.loadDataShortcut.activated.connect(self.load_data)

        toggleCopySeq = QKeySequence(Qt.CTRL + Qt.Key_C)
        self.toggleCopyShortcut = QShortcut(toggleCopySeq, self)
        self.toggleCopyShortcut.activated.connect(self.toggleCopyMode)

        # Tree view for user's sorting shortcuts:
        self.tree = CustomTreeWidget()
        self.tree.setStyleSheet(f"""
            QTreeWidget {{
                border: 1px solid black;
                border-radius: 10px;
                background-color: {Styles.widgetsBgColor};
                color: black;
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

        self.tree.setGraphicsEffect(Styles.getShadowEffect())
        self.tree.setMaximumWidth(250)
        leftInnerLayout.addWidget(self.tree)
        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Shortcut", "Directory", "Actions"])
        self.tree.setColumnWidth(0, 90)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 50)
        self.tree.setFocusPolicy(Qt.NoFocus)
        self.update_tree_view()

        self.clearButton = QPushButton("&Clear tree", self)
        self.clearButton.clicked.connect(self.clearShortcuts)
        self.clearButton.setFocusPolicy(Qt.NoFocus)
        self.clearButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.clearButton.setGraphicsEffect(Styles.getShadowEffect())
        self.clearButton.setStyleSheet(f"""
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
            background-color: red;
        }}
        """)
        leftInnerLayout.addWidget(self.clearButton)

        # Create main Menu bar
        self._createActions()
        self._createMenuBar()
        self._connectActions()

        self.galleryManager.emptyInboxWidget.selectSourceSignal.connect(self.galleryManager.selectSourceDirectory)
        # self.galleryManager.updatePreview()

        # vvvvvvvv TODO: Remove. [Just for DEBUG]: Manually setting src dir
        # self.galleryManager.setSourcePath("/home/jpeska/Repositories/WorkstationSetup/scripts/image-sorter/testing-data/downloads")
        # self.galleryManager.setSourcePath(r"C:\Users\Kyuubi\Repositories\WorkstationSetup\scripts\image-sorter\testing-data\downloads")
        # self.source_dir_label.setText(f"Source directory: {self.galleryManager.getSourcePath()}")
        # ^^^^^^^^^

        # Sort mode is default mode when app starts
        self.set_sort_mode()
        self.setFocusPolicy(Qt.NoFocus)

        # print("Has focus?", self.hasFocus())
        # print("Focus Widget:", self.focusWidget())

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
        if self.shortcutManager.areShortcutsModified():
            self.shortcutManager.saveShortcuts()

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

    # TODO: Telo presunout do CustromTreeWidget a sem pridat pouze volani teze funkce v customtreewidgetu.
    def update_tree_view(self, root:str=None):
        # Just flush the whole content of the tree and rebuild it from scratch.
        self.tree.clear()
        items = []
        shortcuts_data = self.shortcutManager.getData()

        for key_L1, values_L1 in shortcuts_data["keys"].items():
            # print("Key a value", key, values)

            # TODO: Do not show subtrees except the one starting with the first pressed key.
            # if root is not None and key_L1 != root:
            #     continue

            dst_path_L1 = values_L1["dst_path"]
            item_L1 = QTreeWidgetItem([key_L1, Path(dst_path_L1).name])
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
        self.shortcutManager.saveShortcuts()

    def load_data(self):
        if not self.shortcutManager.loadShortcuts():
            return
        self.update_tree_view()

    def clearShortcuts(self):
        self.shortcutManager.askSaveIfChanged()
        self.shortcutManager.setDataUnmodified()
        self.shortcutManager.clearShortcuts()
        self.update_tree_view()

    def undo_last_operation(self):
        print("Undo last operation")
        # print(self.mv_history)

        if not self.mvHistory:
            print(f"History is Empty!")
            return

        imageName = self.mvHistory[-1]["image"]
        src = self.mvHistory[-1]["dst"]
        dst = self.mvHistory[-1]["src"]
        positionIndex = self.mvHistory[-1]["gallery_index"]

        if not os.path.exists(dst):
            print(f"ERROR: Destination directory {dst} does not exist.")
            self.statusBarLabel.setText(f"ERROR: Destination directory {dst} does not exist.")
            self.keySeq = ""
            self.updateKeySequenceLabel()
            return

        # Check that image was not removed from outside of an app
        if not os.path.exists(src + "/" + imageName):
            self.galleryManager.removeFile(imageName)
            self.statusBarLabel.setText(f"File was not found. Probably was removed outside of the app.")
            self.galleryManager.updateCounterLabelText()
            self.galleryManager.updatePreview()
            # Remove last record from history
            if self.mvHistory:
                self.mvHistory.pop()
            self.keySeq = ""
            self.updateKeySequenceLabel()
            return

        # Prevent override of an image in dst, if file with same name exist there.
        if os.path.exists(dst + "/" + imageName):
            self.statusBarLabel.setText(f"File with that name already exists in the dst directory.")
            # TODO: Add random suffix number to the filename (and update name in the list!)
            # for now:
            self.keySeq = ""
            self.updateKeySequenceLabel()
            return

        shutil.move(src + "/" + imageName, dst + "/" + imageName)
        self.statusBarLabel.setText(f"File moved BACK From: {src}.")

        # Remove current image from the list of images in src directory
        self.galleryManager.addFile(imageName, positionIndex)

        # Update counter label
        self.galleryManager.updateCounterLabelText()

        # Remove last record from history
        if self.mvHistory:
            self.mvHistory.pop()

        # Show new image
        self.galleryManager.updatePreview()
        # print(self.images)

    def toggleCopyMode(self):
        # self.next_image_button.setFocus()
        if self.copyOnly is False:
            print("Current mode: Copy")
            self.copyOnly = True
            self.copyButton.setStyleSheet(f"""
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

            self.galleryManager.mediaContainerWidget.setCopyModeBorderHighlight()
            return

        if self.copyOnly is True:
            print("Current mode: Move")
            self.copyOnly = False
            self.copyButton.setStyleSheet(f"""
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

            self.galleryManager.mediaContainerWidget.unsetCopyModeBorderHighlight()
            return

    def set_edit_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Edit")
        self.currentMode = "edit"
        self.editButton.setStyleSheet(f"""
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
        self.sortButton.setStyleSheet(f"""
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
        self.currentMode = "sort"
        self.editButton.setStyleSheet(f"""
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
        self.sortButton.setStyleSheet(f"""
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
        self.galleryManager.updatePreview()

    def handleEditMode(self, event):
        pressedKey = event.text()
        match event.key():
            case Qt.Key_Escape:
                # self.key_seq_history.append(self.key_seq)  # What was purpose of this???
                self.keySeq = ""
                self.updateKeySequenceLabel()

            # Confirm entered shortcut
            case Qt.Key_Return:  # "Return" is the "Enter" key in the center of keyboard.
                print("ENTER: seq:", self.keySeq)
                if len(self.keySeq) == 0:
                    print(f"probably empty (Key seq: {self.keySeq})")
                    return

                # Check, whether sequence contains '-', and if so
                # consider this as removing all shortcuts after the '-' character.
                if "-" in self.keySeq:
                    self.shortcutManager.removeShortcutSequence(self.keySeq)
                    self.keySeq = ""
                    self.update_tree_view()
                    self.updateKeySequenceLabel()
                    self.galleryManager.setFocus(True)  # Return focus to the gallerymanager
                    return

                # Add new shortcut sequence
                for k in self.keySeq:
                    self.shortcutManager.addShortcut(self.keySeq)

                dstSortDirectory = QFileDialog.getExistingDirectory(self, "Select Directory")
                self.shortcutManager.addDstPathForShortcut(self.keySeq, dstSortDirectory)
                self.keySeq = ""
                self.updateKeySequenceLabel()
                self.update_tree_view()
                print(json.dumps(self.shortcutManager.getData(), indent=2))
                self.galleryManager.setFocus(True)  # Return focus to the gallerymanager

            case _:
                self.keySeq += pressedKey
                self.updateKeySequenceLabel()

    def handleSortMode(self, event):
        pressedKey = event.text()
        # Cancel currently started shortcut or escape from the hold partial sequence
        match event.key():
            case Qt.Key_Escape:
                print("ESC")
                # print("key_seq:", self.key_seq)
                # print("permanent_key_seq:", self.permanent_key_seq)
                if self.keySeq and self.permanentKeySeq:
                    self.keySeq = ""
                elif not self.keySeq and self.permanentKeySeq:
                    self.permanentKeySeq = ""
                elif self.keySeq and not self.permanentKeySeq:
                    self.keySeq = ""
                else:
                    pass
                self.updateKeySequenceLabel()

            # Hold current shortcut and use it as default for upcoming sequences until escape
            case Qt.Key_Return:  # Key_Return is non-numeric Enter key
                print("ENTER")

                if self.keySeq:
                    self.permanentKeySeq = self.keySeq
                    self.keySeq = ""

                self.updateKeySequenceLabel()

            # Single-time move file
            case Qt.Key_Space:
                print("Select destination directory just for the current image.")

                dst = ""

                # TODO: Refactor:
                # If keySeq is empty, pressing "space" will allow user to select dst dir for one-time use.
                # and else dst directory is chosen from the current non-terminal shortcut, if dst_path is not empty.
                if self.keySeq:
                    print(f"keySeq is not empty ('{self.keySeq}')")
                    nonTerminalKey = self.shortcutManager.getLastKeyContentOfSequence(self.keySeq)
                    if nonTerminalKey:
                        dst = nonTerminalKey["dst_path"]
                        if not os.path.exists(dst):
                            print(f"Shortcut probably does not contain dst_path ({dst}).")
                            return
                        print("middle_path", dst)
                    else:
                        print(f"Shortcut sequence {self.keySeq} does not exist.")
                        return

                else:  # KeySeq is empty
                    singleUseDstDirectory = QFileDialog.getExistingDirectory(self, "Select Directory")

                    # Check that some directory was selected
                    if not singleUseDstDirectory:
                        self.statusBarLabel.setText(f"No directory was selected.")
                        return

                    print(singleUseDstDirectory)
                    dst = singleUseDstDirectory

                src = self.galleryManager.getSourcePath()
                imageName = self.galleryManager.getCurrentFilename()

                # Check that image was not removed from outside of an app
                if not imageName or not os.path.exists(src + "/" + imageName):
                    self.galleryManager.removeFile(imageName)
                    self.statusBarLabel.setText(f"File was not found. Probably was removed outside of the app.")
                    self.galleryManager.updateCounterLabelText()
                    self.galleryManager.updatePreview()
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if os.path.exists(dst + "/" + imageName):
                    self.statusBarLabel.setText(f"File with that name already exists in the dst directory.")
                    # TODO: Add random suffix number to the filename (and update name in the list!)
                    # for now:
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Remove current image from the list of images in src directory
                if not self.copyOnly:
                    self.galleryManager.removeFile(imageName)
                    shutil.move(src + "/" + imageName, dst + "/" + imageName)
                    self.mvHistory.append({"src": src, "dst": dst, "image": imageName, "gallery_index": self.galleryManager.getGalleryIndex()})
                    self.statusBarLabel.setText(f"File moved to {dst}.")
                else:
                    shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                    self.galleryManager.decrementGalleryIndex()
                    self.statusBarLabel.setText(f"File copied to {dst}.")

                self.keySeq = ""
                self.updateKeySequenceLabel()
                self.galleryManager.updateCounterLabelText()

                # Show new image
                self.galleryManager.updatePreview()

            # Repeat last move from src to dst of current image.
            case Qt.Key_Period:
                print("Repeat last finished command for current image")

                if len(self.mvHistory) <= 0 or len(self.keySeqHistory) <= 0:
                    print("History is empty.")
                    return

                print(f"Last history entry: {self.keySeqHistory[-1]}")

                imageName = self.galleryManager.getCurrentFilename()

                src = self.mvHistory[-1]["src"]
                dst = self.mvHistory[-1]["dst"]

                if not os.path.exists(dst):
                    print(f"ERROR: Destination directory {dst} does not exist.")
                    self.statusBarLabel.setText(f"ERROR: Destination directory {dst} does not exist.")
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Check that image was not removed from outside of an app
                if not os.path.exists(src + "/" + imageName):
                    self.galleryManager.removeFile(imageName)
                    self.statusBarLabel.setText(f"File was not found. Probably was removed outside of the app.")
                    self.galleryManager.updateCounterLabelText()
                    self.galleryManager.updatePreview()
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if os.path.exists(dst + "/" + imageName):
                    self.statusBarLabel.setText(f"File with that name already exists in the dst directory.")
                    # TODO: Add random suffix number to the filename (and update name in the list!)
                    # for now:
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Remove current image from the list of images in src directory
                if not self.copyOnly:
                    self.galleryManager.removeFile(imageName)
                    shutil.move(src + "/" + imageName, dst + "/" + imageName)
                    self.mvHistory.append({"src": src, "dst": dst, "image": imageName, "gallery_index": self.galleryManager.getGalleryIndex()})
                    self.statusBarLabel.setText(f"File moved to {dst}.")
                else:
                    shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                    self.galleryManager.incrementGalleryIndex()
                    self.statusBarLabel.setText(f"File copied to {dst}.")

                self.galleryManager.updateCounterLabelText()

                # Show new image
                self.galleryManager.updatePreview()


            case Qt.Key_Delete:
                if self.galleryManager.isGalleryEmpty():
                    print("Source directory is empty")
                    return

                imageName = self.galleryManager.getCurrentFilename()
                src = self.galleryManager.getSourcePath()
                dst = src + "/" + "__DELETED__"

                if not os.path.exists(dst):
                    os.makedirs(dst)

                # Check that image was not removed from outside of an app
                if not os.path.exists(src + "/" + imageName):
                    self.galleryManager.removeFile(imageName)
                    self.statusBarLabel.setText(f"File was not found. Probably was removed outside of the app.")
                    self.galleryManager.updateCounterLabelText()
                    self.galleryManager.updatePreview()
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if os.path.exists(dst + "/" + imageName):
                    self.statusBarLabel.setText(f"File with that name already exists in the dst directory.")
                    # TODO: Add random suffix number to the filename (and update name in the list!)
                    # for now:
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                print(f"It is found. Possible to move from {self.galleryManager.getSourcePath()} into {dst}!")

                # Remove current image from the list of images in src directory
                self.galleryManager.removeFile(imageName)
                shutil.move(src + "/" + imageName, dst + "/" + imageName)
                self.mvHistory.append({"src": src, "dst": dst, "image": imageName, "gallery_index": self.galleryManager.getGalleryIndex()})
                self.statusBarLabel.setText(f"File Deleted.")

                self.galleryManager.updateCounterLabelText()

                # Show new image
                self.galleryManager.updatePreview()

            case _: # Other keys
                if event.key() not in allowedKeys:
                    print("not a-z was pressed, nothing to append to shortcuts.")
                    return

                self.keySeq += pressedKey

                # self.update_tree_view(event.key()) # TODO:

                fullShortcut = ""
                if self.permanentKeySeq:
                    fullShortcut = self.permanentKeySeq + self.keySeq
                else:
                    fullShortcut = self.keySeq

                print("key_seq:", self.keySeq)
                print("full key_seq:", fullShortcut)

                # print("dst for shortcut:", self.shortcut_manager.get_dst_for_shortcut(full_shortcut))
                if not self.keySeq:
                    return

                dstPath = self.shortcutManager.getDstPathForShortcut(fullShortcut)
                if dstPath:
                    print("HIT!")

                    if self.galleryManager.isGalleryEmpty():
                        print("Source directory is empty")
                        self.keySeq = ""
                        self.updateKeySequenceLabel()
                        return

                    imageName = self.galleryManager.getCurrentFilename()
                    src = self.galleryManager.getSourcePath()
                    dst = dstPath

                    if not os.path.exists(dst):
                        print(f"ERROR: Destination directory {dst} does not exist.")
                        self.statusBarLabel.setText(f"ERROR: Destination directory {dst} does not exist.")
                        self.keySeq = ""
                        self.updateKeySequenceLabel()
                        return

                    # Check that image was not removed from outside of an app
                    if not os.path.exists(src + "/" + imageName):
                        self.galleryManager.removeFile(imageName)
                        self.statusBarLabel.setText(f"File was not found. Probably was removed outside of the app.")
                        self.galleryManager.updateCounterLabelText()
                        self.galleryManager.updatePreview()
                        self.keySeq = ""
                        self.updateKeySequenceLabel()
                        return

                    # Prevent override of an image in dst, if file with same name exist there.
                    if os.path.exists(dst + "/" + imageName):
                        self.statusBarLabel.setText(f"File with that name already exists in the dst directory.")
                        # TODO: Add random suffix number to the filename (and update name in the list!)
                        # for now:
                        self.keySeq = ""
                        self.updateKeySequenceLabel()
                        return

                    self.keySeqHistory.append(fullShortcut)

                    print(f"It is found. Possible to move from {self.galleryManager.getSourcePath()} into {dst}!")

                    # Remove current image from the list of images in src directory
                    if not self.copyOnly:
                        self.galleryManager.removeFile(imageName)
                        shutil.move(src + "/" + imageName, dst + "/" + imageName)
                        self.mvHistory.append({"src": src, "dst": dst, "image": imageName, "gallery_index": self.galleryManager.getGalleryIndex()})
                        self.statusBarLabel.setText(f"File moved to {dst}.")
                    else:
                        shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                        self.galleryManager.incrementGalleryIndex()
                        self.statusBarLabel.setText(f"File copied to {dst}.")

                    # Update counter label TODO fix:
                    self.galleryManager.updateCounterLabelText()

                    # Show new image
                    self.galleryManager.updatePreview()

                    # Enable temporaly save and reuse partial shortcut
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                else:
                    self.updateKeySequenceLabel()


    def keyPressEvent(self, event):
        if not isinstance(event, QKeyEvent):
            return
        
        pressedKey = event.text()
        print("Pressed Key:", pressedKey)

        # Key binding working in both modes:
        match event.key():
            case Qt.Key_Left:
                # TODO: de-chain: 
                # self.showPreviousImage()
                self.galleryManager.mediaContainerWidget.showPreviousImage()

            case Qt.Key_Right:
                # TODO de-chain:
                # self.showNextImage()
                self.galleryManager.mediaContainerWidget.showNextImage()

            case Qt.Key_Home:
                # TODO: de-chain:
                self.galleryManager.mediaContainerWidget.showFirstImage()

            case Qt.Key_End:
                # TODO de-chain:
                self.galleryManager.mediaContainerWidget.showLastImage()

            case Qt.Key_Delete:
                # TODO
                pass

            case _: # Default case
                super().keyPressEvent(event)

        if self.currentMode == "edit":
            self.handleEditMode(event)

        elif self.currentMode == "sort":
            self.handleSortMode(event)
        
        else: # Unknown mode
            pass

    def updateKeySequenceLabel(self):
        separator = "+"
        if self.permanentKeySeq:
            self.keyLabel.setText(f"Key Sequence Pressed: \n{self.permanentKeySeq}{separator}{self.keySeq}")
        else:
            self.keyLabel.setText(f"Key Sequence Pressed: \n{self.keySeq}")

    def updateStatusBarLabel(self, src, dst):
        self.statusBarLabel.setText(f"File copied to {dst}.")

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
    app.aboutToQuit.connect(window.shortcutManager.askSaveIfChanged)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

