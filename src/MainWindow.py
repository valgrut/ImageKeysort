import sys
import json
import datetime
import typing
import logging

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject, QSize
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
    QMessageBox,
    QToolBar,
    QApplication,
    QStatusBar
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
from src.EditModeHandler import EditModeHandler
from src.Modes import Modes
from src.TextExtractor import TextExtractor

from src.treeView import ShortcutsTreeView

# TODO: Tohle jinam; Kam?
screenWidth = 1152
screenHeight = 864

allowedKeys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
                Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
                Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z, Qt.Key_Escape, Qt.Key_Backspace,
               Qt.Key_Return, Qt.Key_Space, Qt.Key_Period, Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End]

log = logging.getLogger(__name__)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow, QObject):

    previousImageRequestedSignal = pyqtSignal()
    nextImageRequestedSignal = pyqtSignal()
    firstImageRequestedSignal = pyqtSignal()
    lastImageRequestedSignal = pyqtSignal()

    def __init__(self, parent=None, args=None):
        super().__init__(parent)
        super().__init__()

        # ========== CLI argument passing ==========
        srcPathArg = None
        presetsArg = None
        setCopyModeArg = None
        if args is not None:
            srcPathArg = args.src_path
            presetsArg = args.presets_path
            setCopyModeArg = args.set_copy_mode

            log.info(f"Arguments:\n"
                     f" Source path: {srcPathArg}\n"
                     f" Presets:     {presetsArg}\n"
                     f" Copy mode:   {setCopyModeArg}")

        
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
        self.editModeHandler = EditModeHandler(self, self.shortcutManager, self.galleryManager)  # deps are injected
        self.textExtractor = TextExtractor(self.galleryManager)


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

        #self.statusBarLabel = QLabel("Status bar")
        self.statusBarLabel = QStatusBar()
        # self.statusBarLabel.addPermanentWidget(QLabel())
        self.statusBarLabel.setObjectName("statusBarLabel")
        self.statusBarLabel.setGraphicsEffect(Styles.getShadowEffect())
        #self.statusBarLabel.setWordWrap(True)
        self.updateStatusBarLabel(f"App loaded.")
        rightInnerLayout.addWidget(self.statusBarLabel)

        # Left side of the main layout
        self.keyLabel = QLabel("Key Sequence Pressed: \nNone")
        self.keyLabel.resize(self.keyLabel.sizeHint())
        self.keyLabel.setGraphicsEffect(Styles.getShadowEffect())
        self.keyLabel.setObjectName("keyLabel")
        self.keyLabel.setAlignment(Qt.AlignCenter)

        # TODO: WIP
        self.expProgress = QProgressBar()
        self.expProgress.setValue(20)

        self._createActions()

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

        self.clearTreeButton = QPushButton("&Clear tree", self)
        self.clearTreeButton.setObjectName("clearTreeButton")
        # self.clearTreeButton.clicked.connect(self.clearShortcuts)
        self.clearTreeButton.clicked.connect(self.clearTreeAction.activate)
        self.clearTreeButton.setFocusPolicy(Qt.NoFocus)
        self.clearTreeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.clearTreeButton.setGraphicsEffect(Styles.getShadowEffect())

        self.dropChangesTreeButton = QPushButton("&Reload tree", self)
        self.dropChangesTreeButton.setObjectName("dropChangesTreeButton")
        self.dropChangesTreeButton.setToolTip("Drops unsaved changes in the shortcut tree. Effectively reloads shortcuts from the file.")
        self.dropChangesTreeButton.setFocusPolicy(Qt.NoFocus)
        self.dropChangesTreeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.dropChangesTreeButton.setGraphicsEffect(Styles.getShadowEffect())

        leftInnerButtonLayout = QHBoxLayout()
        leftInnerButtonLayout.addWidget(self.editButton)
        leftInnerButtonLayout.addWidget(self.sortButton)

        leftInnerLayout.addWidget(self.expProgress)
        leftInnerLayout.addWidget(self.copyButton)
        leftInnerLayout.addLayout(leftInnerButtonLayout)
        leftInnerLayout.addWidget(self.keyLabel)


        # ========== Default variables and behaviour ==========
        self.currentMode = "home"  # Next options: edit, sort


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
        # Puvodni verze:
        self.treeViewWidget = CustomTreeWidget(self.shortcutManager)
        self.treeViewWidget.setColumnCount(3)
        self.treeViewWidget.setHeaderLabels(["Shortcut", "Directory", "Actions"])
        self.treeViewWidget.setColumnWidth(0, 90)
        self.treeViewWidget.setColumnWidth(1, 100)
        self.treeViewWidget.setColumnWidth(2, 50)

        # TODO: Rewrite, then use.
        #self.treeViewWidget = ShortcutsTreeView(self.shortcutManager)

        self.treeViewWidget.setGraphicsEffect(Styles.getShadowEffect())
        self.treeViewWidget.setMaximumWidth(250)
        leftInnerLayout.addWidget(self.treeViewWidget)
        self.treeViewWidget.setFocusPolicy(Qt.NoFocus)
        self.treeViewWidget.update_tree_view()

        # Add clear button below the Tree
        treeButtonsLayout = QHBoxLayout()
        treeButtonsLayout.addWidget(self.clearTreeButton)
        treeButtonsLayout.addWidget(self.dropChangesTreeButton)
        leftInnerLayout.addLayout(treeButtonsLayout)


        # ========== Menu Bar ==========
        # mainWindowWidget.setContextMenuPolicy(Qt.ActionsContextMenu)

        # Create main Menu bar
        self._createMenuBar()

        # ========== Tool Bar ==========
        self.toolbar = QToolBar("Image Keysort Tool bar")
        self.toolbar.setIconSize(QSize(16,16))
        self.addToolBar(self.toolbar)

        self.buttonCropImageAction = QAction(QIcon("Resources/image-crop.png"), "Crop", self)
        self.buttonCropImageAction.setStatusTip("Crop current image.")
        # buttonCropImageAction.triggered.connect(self.toolbar_button_clicked)
        self.buttonCropImageAction.setCheckable(True)
        self.buttonCropImageAction.setShortcut("Ctrl+/")  # Repeat crop se bude delat pomoci Ctrl+.
        self.buttonCropImageAction.setDisabled(True)
        self.toolbar.addAction(self.buttonCropImageAction)

        self.toolbar.addSeparator()

        self.buttonExtractTextAction = QAction(QIcon("Resources/edit-shade.png"), "Extract text", self)
        self.buttonExtractTextAction.setStatusTip("Extract text from the image.")
        # buttonExtractTextAction.triggered.connect(self.galleryManager.currentWidget().imageViewWidget.extractTextFromImage)
        self.buttonExtractTextAction.triggered.connect(self.textExtractor.extractTextFromImage)
        self.buttonExtractTextAction.setShortcut("Ctrl+;")
        self.buttonExtractTextAction.setDisabled(True)
        self.toolbar.addAction(self.buttonExtractTextAction)


        # ========== Signal connections ==========
        self.galleryManager.emptyInboxWidget.selectSourceSignal.connect(self.galleryManager.selectSourceDirectory)  # TODO: do it better
        self.galleryManager.enableExtractTextButtonSignal.connect(lambda: self.buttonExtractTextAction.setDisabled(False))  # 'lambda' creates 'callable' from the setDisabled method.
        self.galleryManager.disableExtractTextButtonSignal.connect(lambda: self.buttonExtractTextAction.setDisabled(True))
        self.galleryManager.enableCropButtonSignal.connect(lambda: self.buttonCropImageAction.setDisabled(False))
        self.galleryManager.disableCropButtonSignal.connect(lambda: self.buttonCropImageAction.setDisabled(True))

        self.previousImageRequestedSignal.connect(self.galleryManager.setPreviousImage)
        self.nextImageRequestedSignal.connect(self.galleryManager.setNextImage)
        self.firstImageRequestedSignal.connect(self.galleryManager.setFirstImage)
        self.lastImageRequestedSignal.connect(self.galleryManager.setLastImage)

        self.shortcutManager.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        self.shortcutManager.updateMainWindowTitleSignal.connect(self.updateWindowTitle)
        self.shortcutManager.updateTreePreviewSignal.connect(self.treeViewWidget.update_tree_view)

        self.sortModeHandler.updateKeySequenceLabelSignal.connect(self.updateKeySequenceLabel)
        self.sortModeHandler.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        self.sortModeHandler.updateTreeViewSignal.connect(self.treeViewWidget.update_tree_view)

        self.editModeHandler.updateKeySequenceLabelSignal.connect(self.updateKeySequenceLabel)
        self.editModeHandler.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        self.editModeHandler.updateTreeViewSignal.connect(self.treeViewWidget.update_tree_view)

        self.textExtractor.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)

        self.dropChangesTreeButton.clicked.connect(self.dropChangesAction.activate)

        # ========== Apply the provided CLI options, if any ==========
        if srcPathArg:
            self.galleryManager.setSourcePath(srcPathArg)
        else:
            log.info("Empty or invalid arg srcDir path")

        # Set shortcuts preset from CLI, if some provided
        if presetsArg:
            self.shortcutManager.loadShortcutsFromFile(presetsArg)
            self.treeViewWidget.update_tree_view()  # TODO: emit signal?
        else:
            log.info("Empty or invalid arg shortcuts path")


        # ========== Start the App with the Sort mode as default ==========
        self.set_sort_mode()
        self.setFocusPolicy(Qt.NoFocus)
        if setCopyModeArg is True:  # --set-copy-mode
            self.setCopyMode()

        # print("Has focus?", self.hasFocus())
        # print("Focus Widget:", self.focusWidget())

        log.info("===================================================")
        log.info("App initialised and started!")


    def _createMenuBar(self):
        menuBar = self.menuBar()

        # File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.openDirectoryAction)
        fileMenu.addAction(self.returnToolbarAction)

        act_settings = QAction(QIcon("Resources/gear.png"), "Settings", self)
        act_settings.setShortcut("Ctrl+,")  # common on mac
        act_settings.triggered.connect(self.open_settings)

        fileMenu.addAction(act_settings)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # Edit menu
        shortcutsMenu = QMenu("&Shortcuts", self)
        menuBar.addMenu(shortcutsMenu)
        shortcutsMenu.addAction(self.undoShortcutModificationAction) # TODO WIP
        shortcutsMenu.addSeparator()
        shortcutsMenu.addAction(self.loadAction)
        shortcutsMenu.addAction(self.saveAction)
        shortcutsMenu.addSeparator()
        shortcutsMenu.addAction(self.dropChangesAction)  # TODO
        shortcutsMenu.addAction(self.clearTreeAction)

        # Edit menu
        galleryMenu = QMenu("&Gallery", self)
        menuBar.addMenu(galleryMenu)
        galleryMenu.addAction(self.undoSortAction)
        galleryMenu.addSeparator()
        galleryMenu.addAction(self.openDirectoryAction)

        # Help menu
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)
        showAboutAction = QAction("About", self)
        showAboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(showAboutAction)

        showShortcutsAction = QAction("Keyboard shortcuts", self)
        showShortcutsAction.triggered.connect(self.showKeyboardShortcuts)
        helpMenu.addAction(showShortcutsAction)


    def _createActions(self):
        self.returnToolbarAction = QAction("&Return toolbar", self)
        self.returnToolbarAction.setStatusTip("Returns toolbar, if closed.")
        self.returnToolbarAction.triggered.connect(self.returnToolbar)

        # TODO(QIcon): self.openDirectoryAction = QAction(QIcon('./assets/new.png'), '&New', self)
        self.openDirectoryAction = QAction("&Open directory", self)
        self.openDirectoryAction.setShortcut('Ctrl+O')
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

        self.undoSortAction = QAction("&Undo move", self)
        # self.undoSortAction.setShortcut('Ctrl+Z')  # TODO: Fix - I want the shortcuts to be shown in the menu.
        self.undoSortAction.setStatusTip("Undo last move/copy operation")
        self.undoSortAction.triggered.connect(self.sortModeHandler.undo_last_operation)

        self.undoShortcutModificationAction = QAction("&Undo modification", self)
        # self.undoShortcutModificationAction.setShortcut('Ctrl+Z')  # TODO: Fix - I want the shortcuts to be shown in the menu.
        self.undoShortcutModificationAction.setStatusTip("Undo last shortcut modification. It could be adding, deleting, ...")
        # self.undoShortcutModificationAction.triggered.connect(TODO)

        self.dropChangesAction = QAction("&Drop unsaved changes", self)
        self.dropChangesAction.setStatusTip("Drop unsaved changes in the shortcut tree.")
        self.dropChangesAction.triggered.connect(self.dropUnsavedChanges)

        self.clearTreeAction = QAction("&Clear tree", self)
        self.clearTreeAction.setStatusTip("Clears all shortcuts from the tree.")
        self.clearTreeAction.triggered.connect(self.clearShortcuts)


    @pyqtSlot(str)
    def updateWindowTitle(self, newTitle):
        self.setWindowTitle(newTitle)


    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.settingsChangedSignal.connect(self.treeViewWidget.update_tree_view)
        dlg.settingsChangedSignal.connect(self.apply_settings)
        dlg.exec()


    def dropUnsavedChanges(self):
        if self.shortcutManager.areShortcutsModified():
            qm = QMessageBox()
            user_confirmed = qm.question(self, '', f"Do you really want to reload shortcuts from the file {self.shortcutManager.srcPathOfLoadedData}?", qm.Yes | qm.No)
            if user_confirmed == qm.No:
                return

        self.shortcutManager.dropUnsavedChanges()
        self.treeViewWidget.update_tree_view()

    @pyqtSlot()
    def apply_settings(self):
        log.info("Apply new settings")
        app = QApplication.instance()
        # app.setPalette(SettingsDialog.settingsGetTheme())
        # app.setPalette(Styles.get_dark_palette())

        # TODO: Maybe, load themes from some directory so users can add custom themes without requiring code change.
        # TODO: Use src.Themes ?
        selectedTheme = SettingsDialog.settingsGetTheme()
        match selectedTheme:
            case "Light":
                app.setPalette(Styles.get_light_palette())
            case "Dark":
                app.setPalette(Styles.get_dark_palette())
            case "Night":
                app.setPalette(Styles.get_night_palette())
            case "Retro":
                app.setPalette(Styles.get_retro_palette())

        import pathlib
        # Required for new styles to take effect.
        app.setStyleSheet(pathlib.Path('static/app-styles.qss').read_text(encoding="utf-8"))


    def showAbout(self):
        aboutBox = QMessageBox(self)
        aboutBox.setWindowTitle("About Image Keysort")
        aboutBox.setObjectName("AboutMessageBox")
        aboutBox.setTextFormat(Qt.RichText)
        with open("about.html", "r", encoding="utf-8") as f:
            about_text = f.read()
        aboutBox.setText(about_text)
        aboutBox.exec()


    def showKeyboardShortcuts(self):
        keyboardShortcutsBox = QMessageBox(self)
        keyboardShortcutsBox.setWindowTitle("Available Keyboard shortcuts")
        keyboardShortcutsBox.setObjectName("KeyboardShortcutsMessageBox")
        keyboardShortcutsBox.setTextFormat(Qt.RichText)
        with open("keyboard_shortcuts.html", "r", encoding="utf-8") as f:
            shortcuts_text = f.read()
        keyboardShortcutsBox.setText(shortcuts_text)
        keyboardShortcutsBox.exec()

    def exitApp(self):
        if self.shortcutManager.areShortcutsModified():
            self.shortcutManager.saveShortcuts()
        # writeSettings()
        # event.accept()

        log.info("Exitting the app.")
        sys.exit(0)
        exit(0)

    def returnToolbar(self):
        self.toolbar.show()

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
        log.info("Toggle Copy mode ON.")
        self.sortModeHandler.setCopyOnly()
        self.copyButton.setChecked(True)
        self.galleryManager.mediaContainerWidget.setCopyModeBorderHighlight()
        return

    def unsetCopyMode(self):
        log.info("Toggle Copy mode OFF.")
        self.sortModeHandler.unsetCopyOnly()
        self.copyButton.setChecked(False)
        self.galleryManager.mediaContainerWidget.unsetCopyModeBorderHighlight()
        return

    @pyqtSlot()
    def toggleCopyMode(self):
        if self.sortModeHandler.getCopyOnlyState() is False:
            self.setCopyMode()
            return

        if self.sortModeHandler.getCopyOnlyState() is True:
            self.unsetCopyMode()
            return

    @pyqtSlot()
    def set_edit_mode(self):
        log.info("Mode Changed to: Edit")
        self.currentMode = Modes.EDIT
        self.editButton.setChecked(True)
        self.sortButton.setChecked(False)
        # self.treeViewWidget.setColumnHidden(2, False)
        self.treeViewWidget.setEnabled(True)

    @pyqtSlot()
    def set_sort_mode(self):
        log.info("Mode Changed to: Sort")
        self.currentMode = Modes.SORT
        self.editButton.setChecked(False)
        self.sortButton.setChecked(True)
        # self.treeViewWidget.setColumnHidden(2, True)
        self.treeViewWidget.setEnabled(True)
        self.galleryManager.updatePreview()

    def keyPressEvent(self, event):
        if not isinstance(event, QKeyEvent):
            return

        pressedKey = event.text()
        # if pressedKey not in self.allowedKeys:
        #     print(f"!!! {pressedKey} not in AllowedKeys.")
        #     return
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

            case _:  # Default case
                super().keyPressEvent(event)

        if self.currentMode == Modes.EDIT:
            self.editModeHandler.handleEditMode(event)

        elif self.currentMode == Modes.SORT:
            self.sortModeHandler.handleSortMode(event)

        else: # Unknown mode
            pass


    @pyqtSlot(str)
    def updateKeySequenceLabel(self, newContent=None):
        if newContent is not None:
            self.keyLabel.setText(newContent)
        else:
            self.keyLabel.setText(f"Key Sequence Pressed: \n")


    @pyqtSlot(str)
    def updateStatusBarLabel(self, message):
        dateNowStr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # self.statusBarLabel.setText(f"[{dateNowStr}]: {message}")
        self.statusBarLabel.showMessage(f"[{dateNowStr}]: {message}")
        # self.statusBarLabel.showMessage(f"[{dateNowStr}]: {message}", 2000)
        # TODO: MAYBE Change into scrollable history of status bar.



