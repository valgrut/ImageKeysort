import sys
import json
import argparse
import datetime
import typing

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QShortcut,
    QMenu,
    QAction,
    QSplitter,
    QProgressBar,
    QMessageBox
)
from PyQt5.QtGui import QKeyEvent, QKeySequence, QCursor, QIcon

# pip3 install pyqt5
# pip3 install keyboard

from src.GalleryManager import GalleryManager
from src.ShortcutManager import ShortcutManager
from src.CustomTreeWidget import CustomTreeWidget
from src.Styles import Styles
from src.SettingsDialog import SettingsDialog
from src.SortModeHandler import SortModeHandler
from src.Modes import Modes

# TODO: Tohle jinam; Kam?
screenWidth = 1152
screenHeight = 864


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow, QObject):

    previousImageRequestedSignal = pyqtSignal()
    nextImageRequestedSignal = pyqtSignal()
    firstImageRequestedSignal = pyqtSignal()
    lastImageRequestedSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        super().__init__()

        # ========== CLI argument parsing ==========
        parser = argparse.ArgumentParser(
                    prog='Image Keysort',
                    description='Shortcut based image sorter.',
                    epilog='For CLI options, please refer to the documentation.')
        parser.add_argument('-c', '--set-copy-mode', action='store_true')  # on/off flag
        parser.add_argument('--src-path', type=str, required=False, help='Path to the source directory')
        parser.add_argument('--presets-path', type=str, required=False, help='Preset file name path')
        args = parser.parse_args()

        srcPathArg = args.src_path
        presetsArg = args.presets_path
        setCopyModeArg = args.set_copy_mode

        print(f"Source path: {srcPathArg}")
        print(f"Presets: {presetsArg}")


        # ========== Main App Window parameters ==========
        self.appTitle = "Image Keysort"
        self.setWindowTitle(self.appTitle)
        self.setWindowIcon(QIcon(':Resources/icon.jpg'))
        self.setMinimumWidth(screenWidth)
        self.setMinimumHeight(screenHeight)


        # ========== Management Objects instantiation ==========
        self.shortcutManager = ShortcutManager(self)  # deps are injected
        self.galleryManager = GalleryManager(self)  # deps are injected
        self.sortModeHandler = SortModeHandler(self, self.shortcutManager, self.galleryManager)  # deps are injected
        self.sortModeHandler.updateKeySequenceLabelSignal.connect(self.updateKeySequenceLabel)
        self.sortModeHandler.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)

        # ========== Layout ==========
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
        self.statusBarLabel.setObjectName("statusBarLabel")
        self.statusBarLabel.setGraphicsEffect(Styles.getShadowEffect())
        self.statusBarLabel.setWordWrap(True)
        rightInnerLayout.addWidget(self.statusBarLabel)

        # Left side of the main layout
        self.keyLabel = QLabel("Key Sequence Pressed: \nNone")
        self.keyLabel.resize(self.keyLabel.sizeHint())
        self.keyLabel.setGraphicsEffect(Styles.getShadowEffect())
        self.keyLabel.setObjectName("keyLabel")
        self.keyLabel.setAlignment(Qt.AlignCenter)

        self.expProgress = QProgressBar()
        self.expProgress.setValue(20)

        self.copyButton = QPushButton("&Copy", self)
        self.copyButton.setCheckable(True)
        self.copyButton.clicked.connect(self.toggleCopyMode)
        self.copyButton.setFocusPolicy(Qt.NoFocus)
        self.copyButton.setGraphicsEffect(Styles.getShadowEffect())
        self.copyButton.setToolTip("Toggle copy mode (switch between copy and move operation).")
        self.copyButton.setCursor(QCursor(Qt.PointingHandCursor))

        self.editButton = QPushButton("&Edit", self)
        self.editButton.setCheckable(True)
        self.editButton.clicked.connect(self.set_edit_mode)
        self.editButton.setFocusPolicy(Qt.NoFocus)
        self.editButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.editButton.setGraphicsEffect(Styles.getShadowEffect())

        self.sortButton = QPushButton("&Sort", self)
        self.sortButton.setCheckable(True)
        self.sortButton.clicked.connect(self.set_sort_mode)
        self.sortButton.setFocusPolicy(Qt.NoFocus)
        self.sortButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.sortButton.setGraphicsEffect(Styles.getShadowEffect())

        self.clearButton = QPushButton("&Clear treeViewWidget", self)
        self.clearButton.setObjectName("clearTreeButton")
        self.clearButton.clicked.connect(self.clearShortcuts)
        self.clearButton.setFocusPolicy(Qt.NoFocus)
        self.clearButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.clearButton.setGraphicsEffect(Styles.getShadowEffect())

        leftInnerButtonLayout = QHBoxLayout()
        leftInnerButtonLayout.addWidget(self.editButton)
        leftInnerButtonLayout.addWidget(self.sortButton)

        leftInnerLayout.addWidget(self.expProgress)
        leftInnerLayout.addWidget(self.copyButton)
        leftInnerLayout.addLayout(leftInnerButtonLayout)
        leftInnerLayout.addWidget(self.keyLabel)


        # ========== Default variables and behaviour ==========
        # self.keySeqHistory = []
        # self.mvHistory = []
        self.keySeq = ""
        # self.permanentKeySeq = ""
        self.currentMode = "home"  # Next options: edit, sort
        # self.copyOnly = False
        print("Mod: " + self.currentMode)


        # ========== Register global keyboard shortcuts ==========
        setEditModeSeq = QKeySequence(Qt.CTRL + Qt.Key_E)
        self.setEditModeShortcut = QShortcut(setEditModeSeq, self)
        self.setEditModeShortcut.activated.connect(self.set_edit_mode)

        setSortModeSeq = QKeySequence(Qt.CTRL + Qt.Key_R)
        self.setSortModeShortcut = QShortcut(setSortModeSeq, self)
        self.setSortModeShortcut.activated.connect(self.set_sort_mode)

        undoSeq = QKeySequence(Qt.CTRL + Qt.Key_Z)
        self.undoShortcut = QShortcut(undoSeq, self)
        self.undoShortcut.activated.connect(self.sortModeHandler.undo_last_operation)

        saveDataSeq = QKeySequence(Qt.CTRL + Qt.Key_S)
        self.saveDataShortcut = QShortcut(saveDataSeq, self)
        self.saveDataShortcut.activated.connect(self.save_data)

        loadDataSeq = QKeySequence(Qt.CTRL + Qt.Key_L)
        self.loadDataShortcut = QShortcut(loadDataSeq, self)
        self.loadDataShortcut.activated.connect(self.load_data)

        toggleCopySeq = QKeySequence(Qt.CTRL + Qt.Key_C)
        self.toggleCopyShortcut = QShortcut(toggleCopySeq, self)
        self.toggleCopyShortcut.activated.connect(self.toggleCopyMode)


        # ========== User's Shortcuts Tree Structure and Viewer ==========
        self.treeViewWidget = CustomTreeWidget(self.shortcutManager)
        self.treeViewWidget.setGraphicsEffect(Styles.getShadowEffect())
        self.treeViewWidget.setMaximumWidth(250)
        leftInnerLayout.addWidget(self.treeViewWidget)
        self.treeViewWidget.setColumnCount(3)
        self.treeViewWidget.setHeaderLabels(["Shortcut", "Directory", "Actions"])
        self.treeViewWidget.setColumnWidth(0, 90)
        self.treeViewWidget.setColumnWidth(1, 100)
        self.treeViewWidget.setColumnWidth(2, 50)
        self.treeViewWidget.setFocusPolicy(Qt.NoFocus)
        self.treeViewWidget.update_tree_view() # TODO: emit signal?

        # Add clear button below the Tree
        leftInnerLayout.addWidget(self.clearButton)


        # ========== Menu Bar ==========
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        self.newAction.setIcon(QIcon(":file-new.svg"))
        self.openAction = QAction(QIcon(":file-open.svg"), "&Open...", self)
        self.saveAction = QAction(QIcon(":file-save.svg"), "&Save", self)
        self.aboutAction = QAction(QIcon(":file-save.svg"), "&About", self)

        # Context menu - right click to open options
        # Setting contextMenuPolicy
        # WIP TODO: A melo by to byt aktivni hlavne po kliknuti pravym na obrazek
        # WIP TODO: prave by nemelo delat to samo, co leve. Omezit "Otevrit slozku" pouze na leve tlacitko.
        # WIP TODO: Kdyz EMPTY, pridat tooltip: Left click to open dir.
        mainWindowWidget.setContextMenuPolicy(Qt.ActionsContextMenu)
        # Populating the widget with actions
        mainWindowWidget.addAction(self.newAction)
        mainWindowWidget.addAction(self.openAction)
        mainWindowWidget.addAction(self.saveAction)

        # Create main Menu bar
        self._createActions()
        self._createMenuBar()


        # ========== Signal connections ==========
        self.galleryManager.emptyInboxWidget.selectSourceSignal.connect(self.galleryManager.selectSourceDirectory)  # TODO: do it better
        self.previousImageRequestedSignal.connect(self.galleryManager.setPreviousImage)
        self.nextImageRequestedSignal.connect(self.galleryManager.setNextImage)
        self.firstImageRequestedSignal.connect(self.galleryManager.setFirstImage)
        self.lastImageRequestedSignal.connect(self.galleryManager.setLastImage)
        self.shortcutManager.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        self.shortcutManager.updateMainWindowTitleSignal.connect(self.updateWindowTitle)


        # ========== Apply the provided CLI options, if any ==========
        if srcPathArg:
            self.galleryManager.setSourcePath(srcPathArg)
        else:
            print("Empty or invalid arg srcDir path")

        # Set shortcuts preset from CLI, if some provided
        if presetsArg:
            self.shortcutManager.loadShortcutsFromFile(presetsArg)
            self.treeViewWidget.update_tree_view()  # TODO: emit signal?
        else:
            print("Empty or invalid arg shortcuts path")


        # ========== Start the App with the Sort mode as default ==========
        self.set_sort_mode()
        self.setFocusPolicy(Qt.NoFocus)
        if setCopyModeArg is True:  # --set-copy-mode
            self.setCopyMode()

        # print("Has focus?", self.hasFocus())
        # print("Focus Widget:", self.focusWidget())


    @pyqtSlot(str)
    def updateWindowTitle(self, newTitle):
        self.setWindowTitle(newTitle)


    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.settingsChangedSignal.connect(self.treeViewWidget.update_tree_view)
        # dlg.settingsChanged.connect(self.apply_settings)
        dlg.exec()


    @pyqtSlot()
    def apply_settings(self, s: dict):
        print(s)
        pass


    def showAbout(self):
        aboutBox = QMessageBox(self)
        aboutBox.setWindowTitle("About Image Keysort")
        aboutBox.setObjectName("AboutMessageBox")
        aboutBox.setTextFormat(Qt.RichText)
        with open("about.html", "r", encoding="utf-8") as f:
            about_text = f.read()
        aboutBox.setText(about_text)
        aboutBox.exec()

    def _createMenuBar(self):
        menuBar = self.menuBar()

        # File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.openDirectoryAction)
        fileMenu.addAction(self.loadAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)

        act_settings = QAction("Settings", self)
        act_settings.setShortcut("Ctrl+,")  # common on mac
        act_settings.triggered.connect(self.open_settings)
        fileMenu.addAction(act_settings)


        # Edit menu
        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)

        editMenu.addAction(self.undoAction)
        
        
        # Help menu
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)
        showAboutAction = QAction("About", self)
        showAboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(showAboutAction)


    def _createActions(self):
        # TODO(QIcon): self.openDirectoryAction = QAction(QIcon('./assets/new.png'), '&New', self)
        self.openDirectoryAction = QAction("&Open directory", self)
        # self.openDirectoryAction.setShortcut('Ctrl+O')  # TODO: Fix - I want the shortcuts to be shown in the menu.
        self.openDirectoryAction.setStatusTip("Open source directory")
        self.openDirectoryAction.triggered.connect(self.galleryManager.selectSourceDirectory)

        self.saveAction = QAction("&Save shortcuts", self)
        # self.saveAction.setShortcut('Ctrl+S')  # TODO: Fix - I want the shortcuts to be shown in the menu.
        self.saveAction.setStatusTip("Save current shortcuts to a file")
        self.saveAction.triggered.connect(self.save_data)
        
        self.loadAction = QAction("&Load shortcuts", self)
        # self.loadAction.setShortcut('Ctrl+L')  # TODO: Fix - I want the shortcuts to be shown in the menu.
        self.loadAction.setStatusTip("Load shortcuts from a file")
        self.loadAction.triggered.connect(self.load_data)
        
        self.exitAction = QAction("&Exit", self)
        self.exitAction.setStatusTip("Exit application")
        self.exitAction.triggered.connect(self.exitApp)
        # self.exitAction.setShortcut('Ctrl+Q')  # TODO: Fix - I want the shortcuts to be shown in the menu.

        self.undoAction = QAction("&Undo", self)
        # self.undoAction.setShortcut('Ctrl+Z')  # TODO: Fix - I want the shortcuts to be shown in the menu.
        self.undoAction.setStatusTip("Undo last move/copy operation")
        self.undoAction.triggered.connect(self.sortModeHandler.undo_last_operation)


    def exitApp(self):
        if self.shortcutManager.areShortcutsModified():
            self.shortcutManager.saveShortcuts()
        # writeSettings()
        # event.accept()

        print("Exiting")
        sys.exit(0)
        exit(0)


    def save_data(self):
        self.shortcutManager.saveShortcuts()

    def load_data(self):
        if not self.shortcutManager.loadShortcutsFromDialogue():
            return
        self.treeViewWidget.update_tree_view() # TODO: emit signal?

    def clearShortcuts(self):
        self.shortcutManager.clearShortcuts()
        self.treeViewWidget.update_tree_view() # TODO: emit signal?  Mozna nahradit toto volani za emit signalu pro update_tree_viw()

    def setCopyMode(self):
        print("Current mode: Copy")
        # self.copyOnly = True
        self.sortModeHandler.setCopyOnly()
        self.copyButton.setChecked(True)
        self.galleryManager.mediaContainerWidget.setCopyModeBorderHighlight()
        return

    def unsetCopyMode(self):
        print("Current mode: Move")
        self.sortModeHandler.unsetCopyOnly()
        self.copyButton.setChecked(False)
        self.galleryManager.mediaContainerWidget.unsetCopyModeBorderHighlight()
        return

    def toggleCopyMode(self):
        # self.next_image_button.setFocus()
        if self.sortModeHandler.getCopyOnlyState() is False:
            self.setCopyMode()
            return

        if self.sortModeHandler.getCopyOnlyState() is True:
            self.unsetCopyMode()
            return

    def set_edit_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Edit")
        self.currentMode = Modes.EDIT
        self.editButton.setChecked(True)
        self.sortButton.setChecked(False)
        self.treeViewWidget.setColumnHidden(2, False)
        self.treeViewWidget.setEnabled(True)

    def set_sort_mode(self):
        # Display a message when the shortcut is activated
        # self.messagae_label.setText("You pressed Ctrl+M!")
        print("New mode: Sort")
        self.currentMode = Modes.SORT
        self.editButton.setChecked(False)
        self.sortButton.setChecked(True)
        self.treeViewWidget.setColumnHidden(2, True)
        self.treeViewWidget.setEnabled(False)
        self.galleryManager.updatePreview()


    def cleanupAndUpdate(self):
        self.keySeq = ""
        self.treeViewWidget.update_tree_view() # TODO: emit signal?
        self.updateKeySequenceLabel()
        self.galleryManager.setFocus(True)  # Return focus to the gallerymanager


    # TODO: Mozna move nejakou cast into shortcutManager. Upravuju strukturu zkratek, nic nepresouvam (obrazky).
    # TODO: NEBO Cela tahle funkce handeEditMode by mohla prave byt treba ve tride EditModeHandler.
    def handleEditMode(self, event):
        pressedKey = event.text()
        match event.key():
            # Clear current key-sequence
            case Qt.Key_Escape:
                # self.key_seq_history.append(self.key_seq)  # What was purpose of this???
                self.keySeq = ""
                self.updateKeySequenceLabel()

            # Remove one character from current key-sequence
            case Qt.Key_Backspace:
                if len(self.keySeq) >= 1:
                    self.keySeq = self.keySeq[:-1]
                    self.updateKeySequenceLabel()

            # Confirm entered shortcut, add into tree and ask for the dst path
            case Qt.Key_Return:  # "Return" is the "Enter" key in the center of keyboard.
                print("ENTER: seq:", self.keySeq)
                if len(self.keySeq) == 0:
                    print(f"probably empty (Key seq: {self.keySeq})")
                    return

                # Check, whether sequence contains '-', and if so
                # consider this as removing all shortcuts after the '-' character.
                if "-" in self.keySeq:
                    self.shortcutManager.removeShortcutSequence(self.keySeq)
                    self.cleanupAndUpdate()
                    return

                if ">" in self.keySeq:
                    print("Note: move key_char elsewhere.")
                    self.shortcutManager.moveShortcutSequence(self.keySeq)
                    self.cleanupAndUpdate()
                    return

                if "/" in self.keySeq:
                    print("Note: change key_char X for key_char Y.")
                    self.shortcutManager.changeShortcutKeyChar(self.keySeq)
                    self.cleanupAndUpdate()
                    return

                # Add new shortcut sequence
                for k in self.keySeq:
                    self.shortcutManager.addShortcut(self.keySeq)

                # set parent's path as default for the dialogue when nesting shortcut
                # Usually when nesting shortcuts, they mirror directories, so it is better to show
                # parent's directory for the new shortcut, because it is probable that target directory is there.
                print("Parents path: Get path for shortcut: ", self.keySeq, self.keySeq[:-1])
                # parentPathAdvice = self.shortcutManager.getDstPathForShortcut(self.keySeq[:-1])
                parentPathAdvice = self.shortcutManager.getLastKeyContentOfSequence(self.keySeq[:-1])
                parentPath = ""
                if parentPathAdvice is not None and "dst_path" in parentPathAdvice:
                    print("Parent's path: ", parentPathAdvice["dst_path"])
                    parentPath = parentPathAdvice["dst_path"]

                dstSortDirectory = QFileDialog.getExistingDirectory(self, "Select Directory", parentPath)
                # WIP: TODO: Zde asi povolit podle Settings. Chci vlastne
                # zabranit i pridani zkratek, takze zpetne je odstranit zase?
                # nebo je pridat az po tom, co se potvrdi, ze je slozka
                # vybrana (neprazdna)?
                # print("DST DIR:", dstSortDirectory)
                # if dstSortDirectory is "" and SettingsDialog.settingsGetAllowNoDest():
                self.shortcutManager.addDstPathForShortcut(self.keySeq, dstSortDirectory)
                # else:
                    # self.shortcutManager.addDstPathForShortcut(self.keySeq, "!PRAZDNA")

                self.cleanupAndUpdate()
                print(json.dumps(self.shortcutManager.getData(), indent=2))

            case _:
                self.keySeq += pressedKey
                self.updateKeySequenceLabel()


    def keyPressEvent(self, event):
        if not isinstance(event, QKeyEvent):
            return

        pressedKey = event.text()
        # print("Pressed Key:", pressedKey)

        # Key binding working in both modes:
        match event.key():
            case Qt.Key_Left:
                self.previousImageRequestedSignal.emit()

            case Qt.Key_Right:
                self.nextImageRequestedSignal.emit()

            case Qt.Key_Home:
                self.firstImageRequestedSignal.emit()

            case Qt.Key_End:
                self.lastImageRequestedSignal.emit()

            case Qt.Key_Delete:
                # TODO
                pass

            case _: # Default case
                super().keyPressEvent(event)

        if self.currentMode == Modes.EDIT:
            self.handleEditMode(event)

        elif self.currentMode == Modes.SORT:
            self.sortModeHandler.handleSortMode(event)

        else: # Unknown mode
            pass
    

    @pyqtSlot(str)
    def updateKeySequenceLabel(self, newContent=None):
        # TODO: this will be called as slot from the [X]SortModeHandler a [ ]EditModeHandler.
        if newContent is not None:
            self.keyLabel.setText(newContent)
        else:
            self.keyLabel.setText(f"Key Sequence Pressed: \n{self.keySeq}")

        
    @pyqtSlot(str)
    def updateStatusBarLabel(self, message):
        dateNowStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.statusBarLabel.setText(f"[{dateNowStr}]: {message}.")
        # TODO: Change into scrollable history of status bar. Change to the signal-slots.


