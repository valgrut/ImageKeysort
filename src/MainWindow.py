import sys
import json
from pathlib import Path
import shutil
import os
import argparse
import datetime

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
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
    QTreeWidget,
    QMessageBox
)
from PyQt5.QtGui import QKeyEvent, QKeySequence, QCursor, QIcon

# pip3 install pyqt5
# pip3 install keyboard

from src.GalleryManager import GalleryManager
from src.ShortcutManager import ShortcutManager
from src.TreeItemWithButtons import TreeItemWithButtons
from src.CustomTreeWidget import CustomTreeWidget
from src.Styles import Styles
from src.SettingsDialog import SettingsDialog

screenWidth = 1152
screenHeight = 864


allowedKeys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
                Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
                Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z]


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
        self.shortcutManager = ShortcutManager(self)
        self.galleryManager = GalleryManager(self)


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
        self.keySeqHistory = []
        self.mvHistory = []
        self.keySeq = ""
        self.permanentKeySeq = ""
        self.currentMode = "home"  # Next options: edit, sort
        self.copyOnly = False
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
        self._connectActions()


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
        aboutBox.setText(
            """
            <h3>Image Keysort</h3>
            <p><b>Author:</b> Jiri Peska</p>
            <p>
                Image Keysort is a keyboard-driven tool for fast sorting and organizing images and videos.
                It lets you define shortcut sequences that map sources to destinations, then fly through
                large folders using only the keyboard.
            </p>
            <p><b>Available shortcuts:</b></p>
            <ul>
                <li><b>[a-zA-Z]+</b> – Add shortcut (Edit mode) / Use shortcut (Sort mode)</li>
                <li><b>[a-zA-Z]?-[a-zA-Z]</b> - Remove key after '-' from key before '-'</li>
                <li><b>Ctrl+C</b> – Toggle copy mode</li>
                <li><b>Ctrl+E</b> – Set Edit mode</li>
                <li><b>Ctrl+R</b> – Set Sort mode</li>
                <li><b>.</b> – Repeat last source → destination transition</li>
                <li><b>Space</b> – One-time move/copy of current item even without a full shortcut sequence</li>
                <li><b>Left/Right arrow</b> – Go to next/previous image in selected directory.</li>
                <li><b>Ctrl+Z</b> – Undo last operation (swap src/dst and re-execute)</li>
                <li><b>Ctrl+L</b> – Load predefined shortcuts</li>
                <li><b>Ctrl+O</b> – Open and load directory as source</li>
                <li><b>Delete</b> – Delete current image/video</li>
                <li><b>Esc</b> – Clear current shortcut sequence</li>
                <li><b>Enter</b> – Insert sentinel (“+”) at current position in the shortcut sequence.<br/>
                    Example: <code>ab&lt;Enter&gt;</code> → <code>ab+</code>, then <code>cd</code> → <code>ab+cd</code>.<br/>
                    Pressing <b>Esc</b> removes only the part after the sentinel, keeping <code>ab+</code> instead of clearing the whole sequence.
                </li>
                <li><b>Ctrl+,</b> – Open settings</li>
            </ul>
            <p><b>Example use-case:</b></p>
            <ul>
                <li>1. <b>Ctrl + E</b> - set edit mode</li>
                <li>2. <b>ic ENTER</b> - add shortcut 'i+c' (Images/Cats) and select target directory for it.</li>
                <li>3. <b>Ctrl + R</b> - set Sort mode</li>
                <li>4. <b>Ctrl + O</b> - Select directory, which you want to sort.</li>
                <li>5. <b>ic</b> - Current image will be moved into directory selected for 'ic' shortcut.</li>
            </ul>
            <p>
                <b>GitHub:</b>
                <a href="https://github.com/valgrut/image-keysort" target="_blank">
                    github.com/valgrut/image-keysort
                </a>
            </p>
            """
        )
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


        # Help menu
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)
        showAboutAction = QAction("About", self)
        showAboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(showAboutAction)


    def exitApp(self):
        if self.shortcutManager.areShortcutsModified():
            self.shortcutManager.saveShortcuts()
        # writeSettings()
        # event.accept()

        print("Exiting")
        sys.exit(0)
        exit(0)

    def _createActions(self):
        self.openDirectoryAction = QAction("&Open directory", self)
        self.saveAction = QAction("&Save shortcuts", self)
        self.loadAction = QAction("&Load shortcuts", self)
        self.exitAction = QAction("&Exit", self)

    def _connectActions(self):
        self.openDirectoryAction.triggered.connect(self.galleryManager.selectSourceDirectory)
        self.saveAction.triggered.connect(self.save_data)
        self.loadAction.triggered.connect(self.load_data)
        self.exitAction.triggered.connect(self.exitApp)

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
        self.copyOnly = True
        self.copyButton.setChecked(True)
        # self.copyButton.setStyleSheet(Styles.getActiveButtonStyles())
        self.galleryManager.mediaContainerWidget.setCopyModeBorderHighlight()
        return

    def unsetCopyMode(self):
        print("Current mode: Move")
        self.copyOnly = False
        self.copyButton.setChecked(False)
        # self.copyButton.setStyleSheet(Styles.getDefaultButtonStyles())
        self.galleryManager.mediaContainerWidget.unsetCopyModeBorderHighlight()
        return

    def toggleCopyMode(self):
        # self.next_image_button.setFocus()
        if self.copyOnly is False:
            self.setCopyMode()
            return

        if self.copyOnly is True:
            self.unsetCopyMode()
            return

    def set_edit_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Edit")
        self.currentMode = "edit"
        self.editButton.setChecked(True)
        self.sortButton.setChecked(False)
        # self.editButton.setStyleSheet(Styles.getActiveButtonStyles())
        # self.sortButton.setStyleSheet(Styles.getDefaultButtonStyles())
        self.treeViewWidget.setColumnHidden(2, False)
        self.treeViewWidget.setEnabled(True)

    def set_sort_mode(self):
        # Display a message when the shortcut is activated
        # self.message_label.setText("You pressed Ctrl+M!")
        print("New mode: Sort")
        self.currentMode = "sort"
        self.editButton.setChecked(False)
        self.sortButton.setChecked(True)
        # self.editButton.setStyleSheet(Styles.getDefaultButtonStyles())
        # self.sortButton.setStyleSheet(Styles.getActiveButtonStyles())
        self.treeViewWidget.setColumnHidden(2, True)
        self.treeViewWidget.setEnabled(False)
        self.galleryManager.updatePreview()

    # TODO: Move do specialni nove tridy pro tyhle move operace
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
            self.updateStatusBarLabel(f"File was not found. Probably was removed outside of the app.")
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
            self.updateStatusBarLabel(f"File with that name already exists in the dst directory.")
            # TODO: Add random suffix number to the filename (and update name in the list!)
            # for now:
            self.keySeq = ""
            self.updateKeySequenceLabel()
            return

        shutil.move(src + "/" + imageName, dst + "/" + imageName)
        self.updateStatusBarLabel(f"File moved BACK From: {src}.")

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

    # TODO: move (nejakou cast) into shortcutManager. Upravuju strukturu zkratek, nic
    # nepresouvam (obrazky).
    def handleEditMode(self, event):
        # TODO: Refactor!!!!!
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
                    self.treeViewWidget.update_tree_view() # TODO: emit signal?
                    self.updateKeySequenceLabel()
                    self.galleryManager.setFocus(True)  # Return focus to the gallerymanager
                    return

                if ">" in self.keySeq:
                    print("Note: move key_char elsewhere.")
                    # TODO

                if "/" in self.keySeq:
                    print("Note: change key_char X for key_char Y.")
                    # TODO

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

                self.keySeq = ""
                self.updateKeySequenceLabel()
                self.treeViewWidget.update_tree_view() # TODO: emit signal?
                print(json.dumps(self.shortcutManager.getData(), indent=2))
                self.galleryManager.setFocus(True)  # Return focus to the gallerymanager

            case Qt.Key_Backspace:
                if len(self.keySeq) >= 1:
                    self.keySeq = self.keySeq[:-1]
                    self.updateKeySequenceLabel()

            case _:
                self.keySeq += pressedKey
                self.updateKeySequenceLabel()

    def moveImageFromTo(self, src, dst):
        pass

    # TODO: Move do specialni nove tridy pro tyhle move operace (alespon to
    # move obrazek x do y). V nove tride udelat metody pro presuny obrazkuuu a
    # odpovidajici kontroly.
    # !!!!! Nebo alespon proste vypreparovat veskere move, bo to je tam asi 6x to
    # same. Takze to extrahovat ven do 1 metody.
    def handleSortMode(self, event):
        # TODO: Refactor!!!!! - extrahvoat do separatni classy, kde se bude
        # parsovat to, co user napsal a zjistovat, jestli chce copy, move >,
        # repeat (.), delete (-), a pod.
        pressedKey = event.text()
        # Cancel currently started shortcut or escape from the hold partial sequence
        match event.key():
            case Qt.Key_Escape:
                print("ESC")
                # print("key_seq:", self.key_seq)
                # print("permanent_key_seq:", self.permanent_key_seq)
                # TODO: Refactor this: pridat flag sentinelExists, bude to
                # srozumitelnejsi.
                if self.keySeq and self.permanentKeySeq:
                    self.keySeq = ""
                elif not self.keySeq and self.permanentKeySeq:
                    self.permanentKeySeq = ""
                elif self.keySeq and not self.permanentKeySeq:
                    self.keySeq = ""
                else:
                    pass
                self.updateKeySequenceLabel()

            case Qt.Key_Backspace:
                if len(self.keySeq) >= 1:
                    self.keySeq = self.keySeq[:-1]
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

                # TODO: Refactor celou tuhle hruzu::::::
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
                        self.updateStatusBarLabel(f"No directory was selected.")
                        return

                    print(singleUseDstDirectory)
                    dst = singleUseDstDirectory

                src = self.galleryManager.getSourcePath()
                imageName = self.galleryManager.getCurrentFilename()

                # Check that image was not removed from outside of an app
                if not imageName or not os.path.exists(src + "/" + imageName):
                    self.galleryManager.removeFile(imageName)
                    self.updateStatusBarLabel(f"File was not found. Probably was removed outside of the app.")
                    self.galleryManager.updateCounterLabelText()
                    self.galleryManager.updatePreview()
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if os.path.exists(dst + "/" + imageName):
                    self.updateStatusBarLabel(f"File with that name already exists in the dst directory.")
                    # TODO: Add random suffix number to the filename (and update name in the list!)
                    # for now:
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Remove current image from the list of images in src directory
                if not self.copyOnly:
                    self.galleryManager.removeFile(imageName)
                    shutil.move(src + "/" + imageName, dst + "/" + imageName)
                    self.mvHistory.append(
                        {
                            "src": src,
                            "dst": dst,
                            "image": imageName,
                            "gallery_index": self.galleryManager.getGalleryIndex()
                        }
                    )
                    self.updateStatusBarLabel(f"File moved to {dst}.")
                else:
                    shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                    if SettingsDialog.settingsGetAutoNextAfterCopy():
                        self.galleryManager.decrementGalleryIndex()

                    self.updateStatusBarLabel(f"File copied to {dst}.")

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
                    self.updateStatusBarLabel(f"ERROR: Destination directory {dst} does not exist.")
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Check that image was not removed from outside of an app
                if not os.path.exists(src + "/" + imageName):
                    self.galleryManager.removeFile(imageName)
                    self.updateStatusBarLabel(f"File was not found. Probably was removed outside of the app.")
                    self.galleryManager.updateCounterLabelText()
                    self.galleryManager.updatePreview()
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if os.path.exists(dst + "/" + imageName):
                    self.updateStatusBarLabel(f"File with that name already exists in the dst directory.")
                    # TODO: Add random suffix number to the filename (and update name in the list!)
                    # for now:
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Remove current image from the list of images in src directory
                if not self.copyOnly:
                    self.galleryManager.removeFile(imageName)
                    shutil.move(src + "/" + imageName, dst + "/" + imageName)
                    self.mvHistory.append(
                        {
                            "src": src,
                            "dst": dst,
                            "image": imageName,
                            "gallery_index": self.galleryManager.getGalleryIndex()
                        }
                    )
                    self.updateStatusBarLabel(f"File moved to {dst}.")
                else:
                    shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                    if SettingsDialog.settingsGetAutoNextAfterCopy():
                        self.galleryManager.incrementGalleryIndex()

                    self.updateStatusBarLabel(f"File copied to {dst}.")

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
                    self.updateStatusBarLabel(f"File was not found. Probably was removed outside of the app.")
                    self.galleryManager.updateCounterLabelText()
                    self.galleryManager.updatePreview()
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if os.path.exists(dst + "/" + imageName):
                    self.updateStatusBarLabel(f"File with that name already exists in the dst directory.")
                    # TODO: Add random suffix number to the filename (and update name in the list!)
                    # for now:
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                    return

                print(f"It is found. Possible to move from {self.galleryManager.getSourcePath()} into {dst}!")

                # Remove current image from the list of images in src directory
                self.galleryManager.removeFile(imageName)
                shutil.move(src + "/" + imageName, dst + "/" + imageName)
                self.mvHistory.append(
                    {
                        "src": src,
                        "dst": dst,
                        "image": imageName,
                        "gallery_index": self.galleryManager.getGalleryIndex()
                    }
                )
                self.updateStatusBarLabel(f"File Deleted.")

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
                        self.updateStatusBarLabel(f"ERROR: Destination directory {dst} does not exist.")
                        self.keySeq = ""
                        self.updateKeySequenceLabel()
                        return

                    # Check that image was not removed from outside of an app
                    if not os.path.exists(src + "/" + imageName):
                        self.galleryManager.removeFile(imageName)
                        self.updateStatusBarLabel(f"File was not found. Probably was removed outside of the app.")
                        self.galleryManager.updateCounterLabelText()
                        self.galleryManager.updatePreview()
                        self.keySeq = ""
                        self.updateKeySequenceLabel()
                        return

                    # Prevent override of an image in dst, if file with same name exist there.
                    if os.path.exists(dst + "/" + imageName):
                        # self.statusBarLabel.setText(f"File with that name already exists in the dst directory.")
                        self.updateStatusBarLabel("File with that name already exists in the dst directory.")
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
                        self.mvHistory.append(
                            {
                                "src": src,
                                "dst": dst,
                                "image": imageName,
                                "gallery_index": self.galleryManager.getGalleryIndex()
                            }
                        )
                        self.updateStatusBarLabel(f"File moved to {dst}.")
                    else:
                        shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                        if SettingsDialog.settingsGetAutoNextAfterCopy():
                            self.galleryManager.incrementGalleryIndex()

                        self.updateStatusBarLabel(f"File copied to {dst}.")

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

    @pyqtSlot(str)
    def updateStatusBarLabel(self, message):
        dateNowStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.statusBarLabel.setText(f"[{dateNowStr}]: {message}.")
        # TODO: Change into scrollable history of status bar. Change to the signal-slots.


