import sys
import datetime
import logging
import os
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject, QSize
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QMenu,
    QAction,
    QProgressBar,
    QMessageBox,
    QToolBar,
    QApplication,
    QStatusBar
)
from PyQt5.QtGui import QKeyEvent, QCursor, QIcon, QPixmap

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
from src.commands.TagCommand import TagCommand
from src.file_operations.TextExtractor import TextExtractor
from src.commands.CropImageCommand import CropImageCommand
from src.CropData import CropData
from src.CommandStack import CommandStack
from src.TagSelectionDialog import TagSelectionDialog
from src.QuickDirectoryCreator import QuickDirectoryDialog
from src.QuickDirectoryShortcutCreator import QuickDirectoryShortcutDialog
from src.commands.RotateImageCommand import ImageRotateCommand

# TODO: Tohle jinam; Kam?
screenWidth = 1152
screenHeight = 864

# https://doc.qt.io/archives/qtforpython-5/PySide2/QtCore/Qt.html
allowedKeysCommon = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
                Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
                Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z, Qt.Key_0, Qt.Key_1, Qt.Key_2, Qt.Key_3,
                Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9]

# TODO: Maybe move into SortModeHandler class
allowedKeysSort = allowedKeysCommon + [Qt.Key_Escape, Qt.Key_Backspace, Qt.Key_Return, Qt.Key_Space, Qt.Key_Period,
                                       Qt.Key_Delete, Qt.Key_Left, Qt.Key_Right, Qt.Key_Home, Qt.Key_End, Qt.Key_Comma,
                                       Qt.Key_Semicolon]

# TODO: Maybe move into EditModeHandler class
allowedKeysEdit = allowedKeysCommon + [Qt.Key_Escape, Qt.Key_Backspace, Qt.Key_Return, Qt.Key_Left, Qt.Key_Right,
                                       Qt.Key_Greater, Qt.Key_Minus, Qt.Key_Slash]


log = logging.getLogger(__name__)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow, QObject):
    """
    [Composition root]
    """

    previousImageRequestedSignal = pyqtSignal()
    nextImageRequestedSignal = pyqtSignal()
    firstImageRequestedSignal = pyqtSignal()
    lastImageRequestedSignal = pyqtSignal()
    updateMediaPreviewSignal = pyqtSignal()
    repeatCropCommandSignal = pyqtSignal()
    setEnabledCursorGuidelinesSignal = pyqtSignal(bool)

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

        # self.commandsStack = QUndoStack(self)
        self.commandsStack = CommandStack()

        # ========== Management Objects instantiation ==========
        self.shortcutManager = ShortcutManager(self)  # deps are injected
        self.galleryManager = GalleryManager(self)  # deps are injected

        self.sortModeHandler = SortModeHandler(self, self.shortcutManager, self.galleryManager)  # deps are injected
        self.editModeHandler = EditModeHandler(self, self.shortcutManager, self.galleryManager)  # deps are injected

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
        # TODO: Tabs - future feature
        # self.galleryTabs = QTabWidget(self)
        # self.galleryTabs.setTabsClosable(True)
        # self.galleryTabs.setShortcutEnabled(True)
        # self.galleryTabs.addTab(self.galleryManager, "gallery 1")
        # self.galleryTabs.addTab(GalleryManager(self), "gallery 2")
        # rightInnerLayout.addWidget(self.galleryTabs)
        rightInnerLayout.addWidget(self.galleryManager)

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

        # Show next available character(s) to continue with pressed shortcut.
        self.availableKeycharsLabel = QLabel("None")
        self.availableKeycharsLabel.resize(self.availableKeycharsLabel.sizeHint())
        self.availableKeycharsLabel.setGraphicsEffect(Styles.getShadowEffect())
        self.availableKeycharsLabel.setObjectName("availableKeychar")
        self.availableKeycharsLabel.setAlignment(Qt.AlignCenter)

        # TODO: WIP
        self.expProgress = QProgressBar()
        self.expProgress.setValue(20)

        self._createActions()

        self.copyButton = QPushButton("&Copy", self)
        self.copyButton.setCheckable(True)
        self.copyButton.clicked.connect(self.toggleCopyModeAction.trigger)
        self.copyButton.setFocusPolicy(Qt.NoFocus)
        self.copyButton.setGraphicsEffect(Styles.getShadowEffect())
        self.copyButton.setToolTip("Toggle copy mode (switch between copy and move operation).")
        self.copyButton.setCursor(QCursor(Qt.PointingHandCursor))

        self.editButton = QPushButton("&Edit", self)
        self.editButton.setCheckable(True)
        self.editButton.clicked.connect(self.setEditMode)
        self.editButton.setFocusPolicy(Qt.NoFocus)
        self.editButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.editButton.setGraphicsEffect(Styles.getShadowEffect())

        self.sortButton = QPushButton("&Sort", self)
        self.sortButton.setCheckable(True)
        self.sortButton.clicked.connect(self.setSortMode)
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
        leftInnerLayout.addWidget(self.availableKeycharsLabel)


        # ========== Default variables and behaviour ==========
        self.currentMode = "home"  # Next options: edit, sort


        # ========== User's Shortcuts Tree Structure and Viewer ==========
        # Puvodni verze:
        self.treeViewWidget = CustomTreeWidget(self.shortcutManager)
        self.treeViewWidget.setColumnCount(3)
        self.treeViewWidget.setHeaderLabels(["Shortcut", "Directory", "Actions"])
        self.treeViewWidget.setColumnWidth(0, 90)
        self.treeViewWidget.setColumnWidth(1, 100)
        self.treeViewWidget.setColumnWidth(2, 50)

        # TODO: Rewrite, then use.
        # 1. New tree - qts example
        # from src.treeView import ShortcutsTreeView
        # self.treeViewWidget = ShortcutsTreeView(self.shortcutManager)

        # 2. New tree - My one
        # self.treeViewWidget = NewTreeView(self.shortcutManager)

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
        self.buttonCropImageAction.setChecked(False)
        self.buttonCropImageAction.setShortcut("Ctrl+/")  # Repeat crop se bude delat pomoci Ctrl+.
        self.buttonCropImageAction.setDisabled(True)
        self.buttonCropImageAction.triggered.connect(self.toggleCropImage)
        self.toolbar.addAction(self.buttonCropImageAction)

        self.buttonRotateImageAction = QAction(QIcon("Resources/arrow-circle-right.png"), "Rotate image right", self)
        self.buttonRotateImageAction.setStatusTip("Rotate image right 90 degrees.")
        # self.buttonRotateImageAction.triggered.connect(self.galleryManager.rotateImageRight)
        self.buttonRotateImageAction.triggered.connect(self.createAndExecuteRotateCommand)
        self.buttonRotateImageAction.setCheckable(True)
        self.buttonRotateImageAction.setShortcut("Ctrl+G")
        # self.buttonRotateImageAction.setDisabled(True)
        self.toolbar.addAction(self.buttonRotateImageAction)

        self.toolbar.addSeparator()

        self.buttonExtractTextAction = QAction(QIcon("Resources/clipboard-pencil.png"), "Extract text", self)
        self.buttonExtractTextAction.setStatusTip("Extract text from the image.")
        # buttonExtractTextAction.triggered.connect(self.galleryManager.currentWidget().imageViewWidget.extractTextFromImage)
        self.buttonExtractTextAction.triggered.connect(self.extractTextFromImage)
        self.buttonExtractTextAction.setShortcut("Ctrl+;")
        self.buttonExtractTextAction.setDisabled(True)
        self.toolbar.addAction(self.buttonExtractTextAction)

        self.toolbar.addAction(self.renameFileAction)


        # ========== Signal connections ==========
        self.galleryManager.emptyInboxWidget.selectSourceSignal.connect(self.selectSourceDirectory)
        self.galleryManager.enableExtractTextButtonSignal.connect(lambda: self.buttonExtractTextAction.setDisabled(False))  # 'lambda' creates 'callable' from the setDisabled method.
        self.galleryManager.disableExtractTextButtonSignal.connect(lambda: self.buttonExtractTextAction.setDisabled(True))
        self.galleryManager.enableCropButtonSignal.connect(lambda: self.buttonCropImageAction.setDisabled(False))
        self.galleryManager.disableCropButtonSignal.connect(lambda: self.buttonCropImageAction.setDisabled(True))

        self.previousImageRequestedSignal.connect(self.galleryManager.setPreviousImage)
        self.nextImageRequestedSignal.connect(self.galleryManager.setNextImage)
        self.firstImageRequestedSignal.connect(self.galleryManager.setFirstImage)
        self.lastImageRequestedSignal.connect(self.galleryManager.setLastImage)

        self.galleryManager.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)

        self.shortcutManager.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        self.shortcutManager.updateMainWindowTitleSignal.connect(self.updateWindowTitle)
        self.shortcutManager.updateTreePreviewSignal.connect(self.treeViewWidget.update_tree_view)
        self.shortcutManager.updateAvailableKeysLabelSignal.connect(self.updateAvailableKeysLabel)

        self.sortModeHandler.updateKeySequenceLabelSignal.connect(self.updateKeySequenceLabel)
        self.sortModeHandler.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        self.sortModeHandler.updateTreeViewSignal.connect(self.treeViewWidget.update_tree_view)

        self.editModeHandler.updateKeySequenceLabelSignal.connect(self.updateKeySequenceLabel)
        self.editModeHandler.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        self.editModeHandler.updateTreeViewSignal.connect(self.treeViewWidget.update_tree_view)

        self.dropChangesTreeButton.clicked.connect(self.dropChangesAction.activate)

        self.galleryManager.requestImageCropSignal.connect(self.createAndExecuteCropCommand)
        self.repeatCropCommandSignal.connect(self.reuseLastCropCommand)
        self.setEnabledCursorGuidelinesSignal.connect(self.galleryManager.setEnabledCursorGuidelinesSignal)


        # ========== Apply the provided CLI options, if any ==========
        if srcPathArg:
            self.galleryManager.setSourcePath(srcPathArg)
            self.commandsStack.clear()
        else:
            log.info("Empty or invalid arg srcDir path")

        # Set shortcuts preset from CLI, if some provided
        if presetsArg:
            self.shortcutManager.loadShortcutsFromFile(presetsArg)
            self.treeViewWidget.update_tree_view()  # TODO: emit signal?
        else:
            log.info("Empty or invalid arg shortcuts path")

        
        self.updateAvailableKeysLabel()


        # ========== Start the App with the Sort mode as default ==========
        self.setSortMode()
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

        appSettingsAction = QAction(QIcon("Resources/gear.png"), "Settings", self)
        appSettingsAction.setShortcut("Ctrl+,")  # common on mac
        appSettingsAction.triggered.connect(self.open_settings)

        fileMenu.addAction(appSettingsAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        # Edit menu - Shortcuts
        shortcutsMenu = QMenu("&Shortcuts", self)
        menuBar.addMenu(shortcutsMenu)
        shortcutsMenu.addAction(self.undoShortcutModificationAction) # TODO WIP
        shortcutsMenu.addSeparator()
        shortcutsMenu.addAction(self.loadAction)
        shortcutsMenu.addAction(self.saveAction)
        shortcutsMenu.addSeparator()
        shortcutsMenu.addAction(self.dropChangesAction)  # TODO
        shortcutsMenu.addAction(self.clearTreeAction)

        # Edit menu - Gallery
        galleryMenu = QMenu("&Gallery", self)
        menuBar.addMenu(galleryMenu)
        galleryMenu.addAction(self.undoSortAction)
        galleryMenu.addSeparator()
        galleryMenu.addAction(self.openDirectoryAction)
        galleryMenu.addAction(self.reloadDirectoryAction)
        galleryMenu.addSeparator()
        galleryMenu.addAction(self.renameFileAction)
        galleryMenu.addAction(self.deleteCurrentFileAction)

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

        self.renameFileAction = QAction(QIcon("Resources/pencil.png"), "&Rename file", self)
        self.renameFileAction.setShortcuts(['Ctrl+F', 'F2'])
        self.renameFileAction.setStatusTip("Rename current file.")
        self.renameFileAction.triggered.connect(self.galleryManager.renameFile)

        self.openDirectoryAction = QAction(QIcon('Resources/inbox-plus.png'), "&Open directory", self)
        self.openDirectoryAction.setShortcut('Ctrl+O')
        self.openDirectoryAction.setStatusTip("Open source directory")
        self.openDirectoryAction.triggered.connect(self.selectSourceDirectory)

        self.saveAction = QAction(QIcon('Resources/disk-pencil.png'), "&Save shortcuts", self)
        self.saveAction.setShortcut('Ctrl+S')
        self.saveAction.setStatusTip("Save current shortcuts to a file")
        self.saveAction.triggered.connect(self.save_data)

        self.loadAction = QAction(QIcon('Resources/disk-arrow.png'), "&Load shortcuts", self)
        self.loadAction.setShortcut('Ctrl+L')
        self.loadAction.setStatusTip("Load shortcuts from a file")
        self.loadAction.triggered.connect(self.load_data)

        self.exitAction = QAction(QIcon('Resources/control-power.png'), "&Exit", self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip("Exit application")
        self.exitAction.triggered.connect(self.exitApp)

        self.undoSortAction = QAction(QIcon('Resources/arrow-circle-left.png'), "&Undo move", self)
        self.undoSortAction.setShortcut('Ctrl+Z')
        self.undoSortAction.setStatusTip("Undo last move/copy operation")
        self.undoSortAction.triggered.connect(self.sortModeHandler.undo_last_operation)

        self.undoShortcutModificationAction = QAction(QIcon('Resources/arrow-circle-left.png'), "&Undo modification", self)
        # self.undoShortcutModificationAction.setShortcut('Ctrl+Z')
        self.undoShortcutModificationAction.setStatusTip("Undo last shortcut modification. It could be adding, deleting, ...")
        # self.undoShortcutModificationAction.triggered.connect(TODO)

        self.dropChangesAction = QAction("&Drop unsaved changes", self)
        self.dropChangesAction.setStatusTip("Drop unsaved changes in the shortcut tree.")
        self.dropChangesAction.triggered.connect(self.dropUnsavedChanges)

        self.clearTreeAction = QAction("&Clear tree", self)
        self.clearTreeAction.setStatusTip("Clears all shortcuts from the tree.")
        self.clearTreeAction.triggered.connect(self.clearShortcuts)

        self.deleteCurrentFileAction = QAction("&Delete file", self)
        self.deleteCurrentFileAction.setStatusTip("Delete current file.")
        self.deleteCurrentFileAction.triggered.connect(self.sortModeHandler.handleKeyDelete)

        self.reloadDirectoryAction = QAction("&Reload directory", self)
        self.reloadDirectoryAction.setStatusTip("Reload to synchronize source directory with images in the app.")
        self.reloadDirectoryAction.triggered.connect(self.galleryManager.loadImagesInDirectory)

        self.toggleCopyModeAction = QAction("&Toggle copy mode", self)
        self.toggleCopyModeAction.setShortcut('Ctrl+C')
        self.toggleCopyModeAction.setStatusTip("Toggle copy mode. Switch between copy and move operation.")
        self.toggleCopyModeAction.triggered.connect(self.toggleCopyMode)
        self.addAction(self.toggleCopyModeAction)  # Needed to make the shortcut work.

        self.switchSortEditModeAction = QAction("&Toggle between edit and sort mode.", self)
        self.switchSortEditModeAction.setShortcut(Qt.Key_Tab)
        self.switchSortEditModeAction.setStatusTip("Toggle between edit and sort mode.")
        self.switchSortEditModeAction.triggered.connect(self.switchSortEditMode)
        self.addAction(self.switchSortEditModeAction)

        self.setEditModeAction = QAction("&Set edit mode", self)
        self.setEditModeAction.setShortcut('Ctrl+E')
        self.setEditModeAction.setStatusTip("Sets Edit mode.")
        self.setEditModeAction.triggered.connect(self.setEditMode)
        self.addAction(self.setEditModeAction)  # Needed to make the shortcut work.

        self.setSortModeAction = QAction("&Set sort mode", self)
        self.setSortModeAction.setShortcut('Ctrl+R')
        self.setSortModeAction.setStatusTip("Sets Sort mode.")
        self.setSortModeAction.triggered.connect(self.setSortMode)
        self.addAction(self.setSortModeAction)  # Needed to make the shortcut work.

        # TODO: WIP; experiment / temporal - Some Tags assigned directly to some shortcut.
        # self.appendTag1Action = QAction("&Append tag: Tag1", self)
        # self.appendTag1Action.setShortcut('Ctrl+T')
        # self.appendTag1Action.triggered.connect(self.appendTagToName)
        # self.addAction(self.appendTag1Action)

        self.appendTagFromDialogAction = QAction("&Select Tag and append", self)
        self.appendTagFromDialogAction.setShortcut('Ctrl+Shift+T')
        self.appendTagFromDialogAction.triggered.connect(self.selectTagFromDialog)
        self.addAction(self.appendTagFromDialogAction)

        self.createQuickDirectoryAction = QAction("&Create quickly new directory", self)
        self.createQuickDirectoryAction.setShortcut('Ctrl+Shift+D')
        self.createQuickDirectoryAction.triggered.connect(self.createQuickDirectory)
        self.addAction(self.createQuickDirectoryAction)

        # TODO: How to undo specific Command performed on current file? Like CropCommand or TagCommand?
        self.undoCommandOnStackAction = QAction("&Undo Command operation on stack", self)
        self.undoCommandOnStackAction.setShortcut('Ctrl+Shift+Z')
        self.undoCommandOnStackAction.triggered.connect(self.undoCommand)
        self.addAction(self.undoCommandOnStackAction)

        # TODO: How to Repeat specific Command performed on current file? Like CropCommand or TagCommand?
        self.repeatCommandOnStackAction = QAction("&Repeat Command operation on stack", self)
        self.repeatCommandOnStackAction.setShortcut('Ctrl+Shift+R')  # TODO: Maybe change shortcut to something else.
        self.repeatCommandOnStackAction.triggered.connect(self.reuseLastCropCommand)  # TODO: Currently repeats Crop command!!!!
        self.addAction(self.repeatCommandOnStackAction)

    def selectSourceDirectory(self):
        self.galleryManager.selectSourceDirectory()
        self.commandsStack.clear()
    
    def extractTextFromImage(self):
        """
        Extract text from the given image
        """
        # TODO: Maybe move to GalleryManager or some FileOperationManager
        textExtractor = TextExtractor(self.galleryManager)
        textExtractor.updateStatusBarLabelSignal.connect(self.updateStatusBarLabel)
        textExtractor.extractTextFromImage()
        textExtractor.updateStatusBarLabelSignal.disconnect(self.updateStatusBarLabel)

    def createAndExecuteRotateCommand(self):
        """
        Rotate image 90 degrees right.
        """
        # TODO: Maybe move to GalleryManager or some FileOperationManager

        currentFile = self.galleryManager.getCurrentGalleryItem()
        rotateCommand = ImageRotateCommand(currentFile)
        # TODO: After inventing, how to manage multiple operations above 1 image, uncomment those 2 lines:
        #   pushed = self.commandsStack.push(rotateCommand)
        #   self.commandsStack.execute(rotateCommand)
        rotateCommand.execute()

        # self.updateMediaPreviewSignal.emit()  # TODO maybe rename to redrawMediaPreview().
        self.galleryManager.updatePreview()

    def createAndExecuteCropCommand(self, commandCropData: CropData):
        """
        Push a new crop command into the command stack or update the existing command if it belongs to the same image.

        Then perform the Crop.
        """
        # TODO: Maybe move to GalleryManager or some FileOperationManager
        cropCommand = CropImageCommand(commandCropData.imageData, commandCropData.cropRectangle, commandCropData.originalImageSize)
        pushed = self.commandsStack.push(cropCommand)
        self.commandsStack.execute(pushed)

        # self.updateMediaPreviewSignal.emit()  # TODO maybe rename to redrawMediaPreview().
        self.galleryManager.updatePreview()

    def undoCommand(self):
        """
        Undo the command performed on the current image.
        """
        # TODO: Maybe move to GalleryManager or some FileOperationManager

        # Get currently shown file's name
        currentFilename = self.galleryManager.getCurrentFilename()

        # Undo and remove command from the stack
        if not self.commandsStack.undo(currentFilename):
            log.info("No command associated with the current image. Cannot undo.")
            return

        # Update image preview after undoing the crop command.
        self.galleryManager.updatePreview()
        self.galleryManager.updateFilenameLabelText()
        self.galleryManager.updateStatusBarLabelSignal.emit("Command was undone successfully.")

    def reuseLastCropCommand(self):
        """
        Enable reuse only if the current image has the same original size as the last command on the stack.
        For the Reuse, last command is used, not any command.
        """
        # TODO: Maybe move to GalleryManager or some FileOperationManager

        log.info("Repeat command from stack on current image.")

        currentFile = self.galleryManager.getCurrentGalleryItem()
        pixmapSize = QPixmap(currentFile.pathAsStr()).size()

        lastCropCommand = self.commandsStack.top()
        if not lastCropCommand:
            log.info("There are no commands to repeat.")
            return

        if lastCropCommand.originalImageSize != pixmapSize:
            log.info("Source image's original size and size of current image's size does not match.")
            return

        cropData = CropData(
            imageData=currentFile,
            cropRectangle=lastCropCommand.absoluteCropRectangle,
            originalImageSize=lastCropCommand.originalImageSize
        )

        log.info(f"RepeatCropCommand emitted! Sending: {lastCropCommand.originalImageSize} and {lastCropCommand.absoluteCropRectangle}")
        self.createAndExecuteCropCommand(cropData)

        log.info(f"Crop repeat successful.")


    def selectTagFromDialog(self):
        # TODO: Maybe move to GalleryManager or some FileOperationManager
        tags = ["work", "family", "anime", "urgent", "todo"]  # TODO: Save/Load from the file

        tagsNotAlreadyUsed = [tag for tag in tags if tag not in self.galleryManager.getCurrentFilename()]
        pickedTag = TagSelectionDialog.selectTag(None, tagsNotAlreadyUsed)

        if pickedTag is None:
            print("No tag selected! Quitting.")
            return

        log.info(f"TagDialog - Selected tag: {pickedTag}")

        finalTagFormat = f"[{pickedTag}]"

        currentFile = self.galleryManager.getCurrentGalleryItem()
        tagCommand = TagCommand(currentFile, finalTagFormat)
        log.info(f"TagCommand created and is ready to be pushed.")

        # TODO: After inventing, how to manage multiple operations above 1 image, uncomment those 2 lines:
        # pushed = self.commandsStack.push(tagCommand)
        # self.commandsStack.execute(pushed)

        # TMP solution. Cannot be undone because it is not pushed to the stack. Ref comment few lines above
        tagCommand.execute()

        self.galleryManager.updateFilenameLabelText()
        self.galleryManager.updateStatusBarLabelSignal.emit("File was renamed successfully.")

        # TODO: Load tags from file or settings, not hardcoded


    def createQuickDirectory(self):
        # TODO: Maybe move to GalleryManager or some FileOperationManager

        # TODO: Prozkouset tyhle 3 verze, ktera bude nejlepsi.

        # Version 1 - Dir only
        #self._createQuickDirectoryOnly()

        # Version 2 - Dir and shortcut
        self._createQuickDirectoryAndShortcut()

        # Version 3 - Dir and shortcut from edit mode
        # self._createQuickDirectoryAndShortcutFromEdit()


    def _createQuickDirectoryOnly(self):
        # TODO: Maybe move to GalleryManager or some FileOperationManager

        newDirName = QuickDirectoryDialog.enterName(None)

        # TODO: strip start/end spaces, verify dir format name (no bullshit in the name)
        if not newDirName:
            print(f"Directory {newDirName} cannot be empty string!")
            return

        src = self.galleryManager.getSourcePath()
        dst = str(src / Path(newDirName))

        if os.path.exists(dst):
            print(f"Directory {newDirName} already exists in {src}!")
            return

        # All checks passed - create a dir and shortcut
        os.makedirs(dst)

        print(f"New directory '{newDirName}' has been created!")


    def _createQuickDirectoryAndShortcut(self):
        """
        Dialogue allows to enter both dir name and shortcut.
        
        TODO: Keep possibility to add just directory without shortcut???
        """
        # TODO: Maybe move to GalleryManager or some FileOperationManager

        shortcut, newDirName = QuickDirectoryShortcutDialog.enterName(None)

        # TODO: strip start/end spaces, verify dir format name (no bullshit in the name)
        if not newDirName:
            print(f"Directory {newDirName} cannot be empty string!")
            return

        src = self.galleryManager.getSourcePath()
        dst = str(src / Path(newDirName))

        if os.path.exists(dst):
            print(f"Directory {newDirName} already exists in {src}!")
            return

        if self.shortcutManager.shortcutExists(shortcut):
            print(f"Shortcut {shortcut} already exists!")
            return

        if len(shortcut) > 5:  # TODO: will there be a nesting limit? Maybe pull from the Settings.
            print(f"Shortcut {shortcut} is too long!")
            return

        # All checks passed - create a dir and shortcut
        os.makedirs(dst)
        self.shortcutManager.addShortcutSequence(shortcut, dst)


        print(f"New directory '{newDirName}' has been created!")


    def _createQuickDirectoryAndShortcutFromEdit(self):
        """
        Add a shortcut into the dialogue (edit-mode -> write shortcut but dont enter, instead hit ctrl+shift+D to open dialogue for that shortcut and enter only dirname)

        TODO: Mozna nejen z edit modu. Asi by bylo lepsi to moct udelat i ze sort. Precejen, kdyz zkratka neexistuje, tak se nehitne.
        """

        # TODO: Maybe move to GalleryManager or some FileOperationManager

        newDirName = QuickDirectoryDialog.enterName(None)
        shortcut = self.editModeHandler.keySeq
        # shortcut = self.sortModeHandler.keySeq

        # TODO: strip start/end spaces, verify dir format name (no bullshit in the name)
        if not newDirName:
            print(f"Directory {newDirName} cannot be empty string!")
            return

        src = self.galleryManager.getSourcePath()
        dst = str(src / Path(newDirName))

        if os.path.exists(dst):
            print(f"Directory {newDirName} already exists in {src}!")
            return

        if not shortcut:
            print(f"Shortcut {shortcut} is empty!")
            return

        if len(shortcut) > 5:  # TODO: will there be a nesting limit? Maybe pull from the Settings.
            print(f"Shortcut {shortcut} is too long!")
            return

        # All checks passed - create a dir and shortcut
        os.makedirs(dst)
        self.shortcutManager.addShortcutSequence(shortcut, dst)

        self.editModeHandler.keySeq = ""
        self.updateKeySequenceLabel("")

        print(f"New directory '{newDirName}' has been created!")

    @pyqtSlot(str)
    def updateWindowTitle(self, newTitle):
        self.setWindowTitle(newTitle)


    def open_settings(self):
        dlg = SettingsDialog(self)
        dlg.settingsChangedSignal.connect(self.treeViewWidget.update_tree_view)
        dlg.settingsChangedSignal.connect(self.updateAvailableKeysLabel)
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
        # app.setStyleSheet(Path('static/app-styles.qss').read_text(encoding="utf-8"))
        # app.setStyleSheet(Path('_internal/static/app-styles.qss').read_text(encoding="utf-8"))
        # TODO: Temporal workaround because of the building process on windows vs linux. It is ugly.
        try:
            app.setStyleSheet(Path('static/app-styles.qss').read_text(encoding="utf-8"))
        except:
            try:
                app.setStyleSheet(Path('_internal/static/app-styles.qss').read_text(encoding="utf-8"))
            except:
                print("Could not load app-styles.qss")


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

    def toggleCropImage(self):
        if self.buttonCropImageAction.isChecked():
            self.buttonCropImageAction.setChecked(True)
            self.setEnabledCursorGuidelinesSignal.emit(False)
            return
        if self.buttonCropImageAction.isChecked() is False:
            self.buttonCropImageAction.setChecked(False)
            self.setEnabledCursorGuidelinesSignal.emit(True)
            return

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
        if self.sortModeHandler.isCopyOnly() is False:
            self.setCopyMode()
            return

        if self.sortModeHandler.isCopyOnly() is True:
            self.unsetCopyMode()
            return

    @pyqtSlot()
    def switchSortEditMode(self):
        if self.currentMode is Modes.EDIT:
            self.setSortMode()
            return
        if self.currentMode is Modes.SORT:
            self.setEditMode()
            return

    @pyqtSlot()
    def setEditMode(self):
        log.info("Mode Changed to: Edit")
        self.currentMode = Modes.EDIT
        self.editButton.setChecked(True)
        self.sortButton.setChecked(False)
        # self.treeViewWidget.setColumnHidden(2, False)
        self.availableKeycharsLabel.setText("Next:\n" + "Disabled in Edit mode!")
        self.galleryManager.setDisabled(True)
        self.treeViewWidget.setEnabled(True)
        self.sortModeHandler.restoreAndCleanup()

    @pyqtSlot()
    def setSortMode(self):
        log.info("Mode Changed to: Sort")
        self.currentMode = Modes.SORT
        self.editButton.setChecked(False)
        self.sortButton.setChecked(True)
        # self.treeViewWidget.setColumnHidden(2, True)
        self.updateAvailableKeysLabel()
        self.treeViewWidget.setEnabled(True)
        self.galleryManager.setDisabled(False)
        self.galleryManager.updatePreview()
        self.editModeHandler.cleanupAndUpdate()

    def keyPressEvent(self, event):
        if not isinstance(event, QKeyEvent):
            return

        log.debug(f"event: {event} ; text: {event.text()} ; key: {event.key()}")

        # pressedKey = event.text()
        pressedKey = event.key()
        if self.currentMode is Modes.SORT:
            if pressedKey not in allowedKeysSort:
                print(f"SortMode: Key {pressedKey} not in AllowedKeys.")
                return
        if self.currentMode is Modes.EDIT:
            if pressedKey not in allowedKeysEdit:
                print(f"EditMode: Key {pressedKey} not in AllowedKeys.")
                return

        # Key binding working in both modes:
        match event.key():
            case Qt.Key_Left:
                self.previousImageRequestedSignal.emit()
                # TODO: ? Move/remove this whole match-cases into QActions, since both keyboard and button execute this.
                return

            case Qt.Key_Right:
                self.nextImageRequestedSignal.emit()
                # TODO: ? Move/remove this whole match-cases into QActions, since both keyboard and button execute this.
                return

            case Qt.Key_Home:
                self.firstImageRequestedSignal.emit()
                # TODO: ? Move/remove this whole match-cases into QActions, since both keyboard and button execute this.
                return

            case Qt.Key_End:
                self.lastImageRequestedSignal.emit()
                # TODO: ? Move/remove this whole match-cases into QActions, since both keyboard and button execute this.
                return

            case _:  # Default case
                super().keyPressEvent(event)
                # Then proceed with the handling Sort or Edit mode... vvv

        # TODO: Rewrite na neco jako:
        # self.currentMode.handleEvent(event)
        # A neco takoveho pouzit na vicero mistech, kde lze overloadnout
        # metoda.
        # Napr pri Ctrl+Z se posle do current modu.
        # Kdyz bude aktualni SortMode, tak se undo presun obrazku
        # Kdyz bude aktualni EditMode, tak se undo zmena ve zkratkach.
        # Taky pridat Redo! Undo a Redo bude pohyb po historii s ukazatelem.
        # Pokud nekdo udela alternativni vetev, puvodni od toho bodu bude
        # smazana.
        if self.currentMode == Modes.EDIT:
            self.editModeHandler.handleEditMode(event)

        elif self.currentMode == Modes.SORT:
            self.sortModeHandler.handleSortMode(event)
            
            # Show all possible available key-chars from shortcuts hierarchy for current key-sequence.
            self.updateAvailableKeysLabel()
        else: # Unknown mode
            pass
    
    @pyqtSlot()
    def updateAvailableKeysLabel(self, newContent=None):
        """
        Construct hint message
        """
        sequencePressed = self.sortModeHandler.getCleanSequence()
        availableKeysList = self.shortcutManager.getPossibleFollowupsKeychars(sequencePressed)
        
        if SettingsDialog.settingsGetSortShortcuts():
            availableKeysList = sorted(availableKeysList, key=lambda x: str.casefold(x[0]))
        
        availableKeysStr: str = " ".join(list(availableKeysList))
        
        # availableKeysHint = sequencePressed + " -> " + availableKeysStr  # V1
        # availableKeysHint = availableKeys  # V2
        availableKeysHint = "Next:\n" + availableKeysStr  # V3
        
        self.availableKeycharsLabel.setText(availableKeysHint)

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



