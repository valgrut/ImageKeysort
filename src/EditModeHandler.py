import json
import typing
import logging

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
)

from src.SettingsDialog import SettingsDialog

# TODO: tohle by melo ovlivnovat i edit mode, ne???
allowedKeys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
                Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
                Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z]

log = logging.getLogger(__name__)


class EditModeHandler(QObject):
    """
    Handle edit mode of the app.
    Executes operations.
    """

    updateTreeViewSignal = pyqtSignal()
    updateKeySequenceLabelSignal = pyqtSignal(str)
    updateStatusBarLabelSignal = pyqtSignal(str)

    def __init__(self, mainWindow, shortcutManager, galleryManager, parent=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.shortcutManager = shortcutManager
        self.galleryManager = galleryManager

        # self.mvHistory = []  # TODO: Change to changeHistory, and consider if here or in ShortcutManager.
        self.keySeq = ""


    def updateKeySequenceLabel(self):
        self.updateKeySequenceLabelSignal.emit(f"Key Sequence Pressed: \n{self.keySeq}")


    def updateStatusBarLabel(self, newStatusbarMessage: str):
        self.updateStatusBarLabelSignal.emit(newStatusbarMessage)


    def cleanupAndUpdate(self):
        self.keySeq = ""
        self.updateTreeViewSignal.emit()
        self.updateKeySequenceLabel()
        self.galleryManager.setFocus(True)  # Return focus to the gallerymanager


    def handleEditMode(self, event):
        pressedKey = event.text()
        log.debug(f"Pressed Key: '{pressedKey}'")

        match event.key():
            # Clear current key-sequence
            case Qt.Key_Escape:
                log.debug("handleEditMode: Case 'Escape'")
                # self.key_seq_history.append(self.key_seq)  # What was purpose of this???
                self.keySeq = ""
                self.updateKeySequenceLabel()

            # Remove one character from current key-sequence
            case Qt.Key_Backspace:
                log.debug("handleEditMode: Case 'Backspace'")
                if len(self.keySeq) >= 1:
                    self.keySeq = self.keySeq[:-1]
                    self.updateKeySequenceLabel()

            # Confirm entered shortcut, add into tree and ask for the dst path
            case Qt.Key_Return:  # "Return" is the "Enter" key in the center of keyboard.
                log.debug("handleEditMode: Case 'Enter' (Key_Return)")
                log.info(f"ENTER pressed. Current key-seqence: '{self.keySeq}'.")
                if len(self.keySeq) == 0:
                    log.info(f"probably empty (Key seq: {self.keySeq})")
                    return

                # Check, whether keySeq contains operation character:
                if "-" in self.keySeq:
                    log.info("Edit Operation: Remove (-)")
                    self.shortcutManager.removeShortcutSequence(self.keySeq)
                    self.cleanupAndUpdate()
                    return

                if ">" in self.keySeq:
                    log.info("Edit Operation: Move (>)")
                    self.shortcutManager.moveShortcutSequence(self.keySeq)
                    self.cleanupAndUpdate()
                    return

                if "/" in self.keySeq:
                    log.info("Edit Operation: Change (/)")
                    self.shortcutManager.changeShortcutKeyChar(self.keySeq)
                    self.cleanupAndUpdate()
                    return

                # No operation character, proceed to add new shortcut.

                # set parent's path (or parent's parent's, ...) as default for the dialogue when nesting shortcuts.
                # When nesting shortcuts, they usually correspond to directory hierarchy, so it is better to show
                # parent's directory for the new shortcut, because it is probable that target directory is there.
                parentPath = ""
                parentPathAdvice = self.shortcutManager.getFirstExistingDstPathFromParents(self.keySeq)
                log.info(f"Find first available dst_path from parents of the shortcut {self.keySeq}.")
                log.debug(f"First available 'dst_path' from parents: {parentPathAdvice}.")

                if parentPathAdvice is not None:
                    log.info(f"Parent's path: {parentPathAdvice}")
                    parentPath = parentPathAdvice

                dstSortDirectory = QFileDialog.getExistingDirectory(self.mainWindow, f"Select Directory for shortcut '{self.keySeq}':", parentPath)
                log.debug(f"Selected directory from Dialogue: {dstSortDirectory}")

                # Settings: Allow empty destination path (no path selected) or dont.
                if not dstSortDirectory and not SettingsDialog.settingsGetAllowNoDest():
                    log.info("No dst selected and empty dst is not allowed. No further action.")
                    self.updateStatusBarLabel("Warning: Empty directory cannot be added. This can be changed in Settings.")
                    self.cleanupAndUpdate()
                    return

                # Adding new shortcut sequence into the tree
                log.info("Dst is not empty or empty path is allowed for new shortcut.")
                # for k in self.keySeq:
                #     self.shortcutManager.addShortcut(self.keySeq)
                self.shortcutManager.addShortcutSequence(self.keySeq)
                self.updateStatusBarLabel(f"Shortcut '{self.keySeq}' has been added!")

                # Decide, whether to add dst_path for new shortcut sequence
                # TODO: Bud ponechat settings, jestli povolovat zmeny, NEBO pridat do stromu button zamecek, ktery zamkne modifikace.
                # TODO: Kruci, ja vlastne chtel pridat moznost Undo changes v shortcuts, takze i lock button, i settings budou asi zbytecne.....
                currentDstPathForShortcut = self.shortcutManager.getDstPathForShortcut(self.keySeq)

                # TODO: Refactor. Myslim ,ze by to slo napsat cisteji, protoze se kod vlastne opakuje v IF, a pak v ELSE po potvrzeni.
                if currentDstPathForShortcut is None or SettingsDialog.settingsGetConfirmToOverride() is False:
                    self.shortcutManager.updateDstPathForShortcut(self.keySeq, dstSortDirectory)
                    self.updateStatusBarLabel(f"Directory for shortcut '{self.keySeq}' has been updated to '{dstSortDirectory}'!")
                else:
                    # TODO: 2. Button do ShortcutTree - Lock shortcuts from modifications (allow only adding new shortcuts).
                    #log.info("Overriding existing dst_path is not allowed. Go to Settings to allow it.")
                    #self.updateStatusBarLabel("Warning: Overriding existing dst_path is not allowed. Go to Settings to allow it.")

                    qm = QMessageBox()
                    user_confirmed = qm.question(self.mainWindow, '', f"Do you want to override dst_path for shortcut {self.keySeq}?", qm.Yes | qm.No)
                    if user_confirmed == qm.Yes:
                        self.shortcutManager.updateDstPathForShortcut(self.keySeq, dstSortDirectory)
                        self.updateStatusBarLabel(f"Directory for shortcut '{self.keySeq}' has been updated to '{dstSortDirectory}'!")
                        # TODO: Mozna jeste nejak udelat, aby se prvne zeptalo, esi chci prepsat dst, az pak vyhodit dialog pro novou dst.
                    else:
                        self.updateStatusBarLabel(f"Directory update for shortcut {self.keySeq} was cancelled by the user.")

                self.cleanupAndUpdate()
                log.info(json.dumps(self.shortcutManager.getData(), indent=2))

            case _:
                log.debug("handleEditMode: Case '_' (some other key)")
                self.keySeq += pressedKey
                self.updateKeySequenceLabel()
