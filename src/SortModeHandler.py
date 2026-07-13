import shutil
import os
from dataclasses import dataclass
from pathlib import Path
import typing
import logging

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QKeyEvent

from src.GalleryItem import GalleryItem
from src.SettingsDialog import SettingsDialog
from src.Operations import Operations

log = logging.getLogger(__name__)

@dataclass
class HistoryEntry:
    imageData: GalleryItem
    srcPath: Path
    dstPath: Path
    galleryIndex: int
    operation: Operations


class MoveHistoryManager:
    def __init__(self):
        self._moveHistory: list[HistoryEntry] = []
        
    def push(self, entry: HistoryEntry):
        self._moveHistory.append(entry)
        
    def getLast(self) -> HistoryEntry:
        if self._moveHistory:
            return self._moveHistory[-1]
        return None
        
    def pop(self) -> HistoryEntry:
        if self._moveHistory:
            return self._moveHistory.pop()
        return None
        
    def top(self) -> HistoryEntry:
        if self._moveHistory:
            return self._moveHistory[-1]
        return None

    def clear(self):
        self._moveHistory.clear()
        
    def len(self) -> int:
        return len(self._moveHistory)
    
    def empty(self) -> bool:
        if len(self._moveHistory) <= 0:
            return True
        return False


class SortModeHandler(QObject):
    """
    Handle sort mode of the app.
    Executes operations.

    Allowed syntax examples: TODO: Double-Check, if all options are listed here.
        abcd
        ,abcd    # Activate Copy mode only for this shortcut and move to next image.
        ;abcd    # Activate Copy mode only for this shortcut and stay on this image.
        ab+cd    # Sentinel working as temporal mark. When shortcut is found, only characters after sentinel are cleared.
        ab+,cd
        ab+;cd
        ,ab+cd   # Becomes ab+,cd
        ;ab+cd   # Becomes ab+;cd
        <space>  # Select manually dst for current picture without using any shortcut
        .        # Repeat last move operation
    """

    updateKeySequenceLabelSignal = pyqtSignal(str)
    updateStatusBarLabelSignal = pyqtSignal(str)
    updateTreeViewSignal = pyqtSignal(str)
    playSoundSignal = pyqtSignal(str)

    def __init__(self, mainWindow, shortcutManager, galleryManager, parent=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.shortcutManager = shortcutManager
        self.galleryManager = galleryManager
        self._historyManager = MoveHistoryManager()

        # TODO: Can be customized from Settings.
        self.separatorChar = "+"
        self._copyAndMoveChar = ","
        self._copyAndStopChar = ";"

        self.keySeq = ""
        self.permanentKeySeq = ""
        self.copyOnly = False
        self.copyAndMove = False
        self.copyAndStop = False

        self.finalSequenceText = self.permanentKeySeq + self.separatorChar + self.keySeq

    def getCleanSequence(self):
        """
        Returns sequence without any markers (sentinel +) or one-time copy markers (,;).

        Used for actual Shortcut searching and validation.
        """
        return self.permanentKeySeq + self.keySeq

    def updateKeySequenceLabel(self):
        shortcutText = ""
        onetimeCopyChar = ""

        if self.copyAndMove:
            onetimeCopyChar = self._copyAndMoveChar
        elif self.copyAndStop:
            onetimeCopyChar = self._copyAndStopChar
        else:
            onetimeCopyChar = ""

        if self.permanentKeySeq:
            # Sentinel (+) is set.
            shortcutText = self.permanentKeySeq + self.separatorChar + onetimeCopyChar + self.keySeq
        else:
            # No sentinel, just shortcut.
            shortcutText = onetimeCopyChar + self.keySeq

        self.updateKeySequenceLabelSignal.emit(f"Key Sequence Pressed: \n{shortcutText}")


    def updateStatusBarLabel(self, newStatusbarMessage: str):
        self.updateStatusBarLabelSignal.emit(newStatusbarMessage)


    def handleKeyEscape(self):
        """
        ESC
        Clears out currently pressed sequence.
        If sentinel is present, only temporal sequence is cleared.
        If temporal part of sequence (after sentinel) is empty, permanent sequence (before sentinel) is cleared too.
        """
        log.debug("handleSortMode: Case 'ESC'")

        # if self.keySeq or self.copyAndMove or self.copyAndStop or not self.permanentKeySeq:
        #     self.copyAndStop = False
        #     self.copyAndMove = False

        if (self.keySeq or self.copyAndMove or self.copyAndStop) and self.permanentKeySeq:
            self.keySeq = ""
            self.copyAndStop = False
            self.copyAndMove = False
        elif not self.keySeq and not self.copyAndMove and not self.copyAndStop and self.permanentKeySeq:
            self.permanentKeySeq = ""
        elif self.keySeq and not self.permanentKeySeq:
            self.keySeq = ""
            self.copyAndStop = False
            self.copyAndMove = False
        else:
            log.info("Both self.keySeq and self.permanentKeySeq are empty, nothing to do")
            self.copyAndStop = False
            self.copyAndMove = False

        self.updateKeySequenceLabel()
        self.updateTreeViewSignal.emit(self.getCleanSequence())


    def handleKeyBackspace(self):
        log.debug("handleSortMode: Case 'Backspace'")
        if len(self.keySeq) >= 1:
            self.keySeq = self.keySeq[:-1]
        elif not self.keySeq and (self.copyAndMove or self.copyAndStop):
            self.copyAndMove = False
            self.copyAndStop = False

        self.updateKeySequenceLabel()
        self.updateTreeViewSignal.emit(self.getCleanSequence())


    def handleKeyReturn(self):
        """
        ENTER
        Adds sentinel (+) serving as a temporal position marker.
        When sentinel is present, pressing ESC does not clear whole sequence, only the part after sentinel.
        """

        log.debug("handleSortMode: Case 'Enter' (Key_Return)")

        if self.permanentKeySeq:
            log.info("Sentinel already exists, cannot add another one.")
            return

        if not self.keySeq:
            log.info(f"Nothing to add before sentinel. Current key-sequence is empty.")
            return

        self.permanentKeySeq = self.keySeq
        self.keySeq = ""

        self.updateKeySequenceLabel()
        self.updateTreeViewSignal.emit(self.getCleanSequence())


    def handleKeySpace(self):
        """
        SPACEBAR

        Allows to use dst directory of uncompleted shortcut.
        e.g. If there is a shortcut "abcd", where b.dst="some_path", pressing only 'ab' will not match a shortcut, because it searches for longest possible match (abcd).

        If keySeq is empty, pressing "space" will allow user to SELECT any destination dir just for this one time via Dialogue window.
        If keySeq is not empty AND current's sequence's dst_path is not empty, dst directory of current unfinished sequence is used for operation.

        TODO: maybe: If keySeq is not empty AND current's sequence's dst_path is empty, dst directory of current unfinished sequence is OFFERED via Dialogue window.
        """
        log.debug("handleSortMode: Case 'Space'")
        log.info("Select destination directory just for the current image.")

        dst = ""
        currentSequence = self.getCleanSequence()
        if currentSequence:
            log.info(f"keySeq is not empty ('{currentSequence}')")
            nonTerminalKey = self.shortcutManager.getLastKeyContentOfSequence(currentSequence)
            if not nonTerminalKey:
                log.info(f"Shortcut sequence {currentSequence} does not exist.")
                return
            
            dst = nonTerminalKey["dst_path"]
            if not os.path.exists(dst):
                log.info(f"No action. Shortcut probably does not contain dst_path '{dst}'.")
                self.updateStatusBarLabelSignal.emit(
                    f"No action. Destination directory '{dst}' for the sequence '{currentSequence}' is empty or does not exist.")
                return
            log.info(f"middle_path {dst}")
            
        else:  # KeySeq is empty
            singleUseDstDirectory = QFileDialog.getExistingDirectory(self.mainWindow, "Select Directory")

            # Check that some directory was selected
            if not singleUseDstDirectory:
                self.updateStatusBarLabel(f"No directory was selected.")
                return

            log.info(singleUseDstDirectory)
            dst = singleUseDstDirectory

        src = str(self.galleryManager.getSourcePath())
        imageName = self.galleryManager.getCurrentFilename()
        currentItem = self.galleryManager.getCurrentGalleryItem()
        if not imageName:
            log.warning("There is no gallery currently opened.")
            self.updateStatusBarLabel(f"There is no gallery currently opened.")
            return

        # Check that image was not removed from outside of an app
        if self.srcImageStillExists(src, imageName) is False:
            self.cleanupMissingImage(imageName)
            self.updateAndCleanup()
            return

        # Prevent override of an image in dst, if file with same name exist there.
        if self.srcImageExistsInDst(dst, imageName):
            self.handleExistingImageInDst()
            self.updateAndCleanup()
            return

        # Remove current image from the list of images in src directory
        if not self.copyOnly and not self.copyAndStop and not self.copyAndMove:
            self.moveImageCommand(src, dst, currentItem)
            self.updateStatusBarLabel(f"Shortcut '{currentSequence}' is used. File moved to '{dst}'.")
        else:
            self.copyImageCommand(src, dst, currentItem)
            self.updateStatusBarLabel(f"Shortcut '{currentSequence}' is used. File copied to '{dst}'.")

            # one-shot copy+stop operation with ';' overrides Settings.
            # if SettingsDialog.settingsGetAutoNextAfterCopy() and not self.copyAndStop:
            if (SettingsDialog.settingsGetAutoNextAfterCopy() or self.copyAndMove) and not self.copyAndStop:
                self.galleryManager.incrementGalleryIndex()  # TODO: v handleOtherKey je increment. wtf?

        # Success
        # Play feedback sound
        # if SettingsDialog.playFeedbackSound(): TODO
        # self.mainWindow.feedbackSound.play()
        self.playSoundSignal.emit("SUCCESS_SOUND")

        # Show new image
        self.galleryManager.updatePreview()

        # Restore clean state of the app
        self.updateAndCleanup()


    def handleKeyPeriod(self):
        """
        Repeat the move/copy with the same dst path as the last command.
        Result is identical, as the same key sequence would be pressed again.

        Copy/Move depends only on the currently active mode, not on the
        mode, in which last operation was performed in.

        Example:
        Last operation was made in copy mode.
        Unset copy mode. Press Period.
        This operation is made in non-copy mode (moves image).
        """
        log.debug("handleSortMode: Case '.'")
        log.info("Repeat last finished command for current image")

        if self._historyManager.empty():
            log.info("History is empty.")
            self.updateStatusBarLabel(f"Cannot repeat last command. History is Empty!")
            return

        imageName = self.galleryManager.getCurrentFilename()
        if not imageName:
            log.warning("There is no gallery currently opened.")
            self.updateStatusBarLabel(f"There is no gallery currently opened.")
            return

        lastEntry = self._historyManager.getLast()
        src = str(lastEntry.srcPath)
        dst = str(lastEntry.dstPath)

        if not self.checkDestinationDirectoryExists(dst):
            return

        # Check that image was not removed from outside of an app
        if self.srcImageStillExists(src, imageName) is False:
            self.cleanupMissingImage(imageName)
            return

        # Prevent override of an image in dst, if file with same name exist there.
        if self.srcImageExistsInDst(dst, imageName):
            self.handleExistingImageInDst()
            return

        # Remove current image from the list of images in src directory
        currentItem = self.galleryManager.getCurrentGalleryItem()
        if not self.copyOnly:
            self.moveImageCommand(src, dst, currentItem)
            self.updateStatusBarLabel(f"Shortcut '{self.keySeq}' is used. File moved to '{dst}'.")
        else:
            self.copyImageCommand(src, dst, currentItem)
            self.updateStatusBarLabel(f"Shortcut '{self.keySeq}' is used. File copied to '{dst}'.")

            if SettingsDialog.settingsGetAutoNextAfterCopy():
                self.galleryManager.incrementGalleryIndex()

        # Success
        log.info(f"History entries: {self._historyManager.len()}")
        self.galleryManager.updateCounterLabelText()

        # Play feedback sound
        # if SettingsDialog.playFeedbackSound(): TODO
        # self.mainWindow.feedbackSound.play()
        self.playSoundSignal.emit("SUCCESS_SOUND")

        # Show new image
        self.galleryManager.updatePreview()

        # Restore clean state of the app
        self.updateAndCleanup()


    def handleKeyDelete(self):
        # TODO: instead of removing the GalleryItem from the availableMediaFiles, move it to deletedMediaFiles.
        # TODO: _deletedMediaFiles pak budou dropnuty, kdyz se zmeni galerie a pod...
        log.debug("handleSortMode: Case 'Delete'")
        if self.galleryManager.isGalleryEmpty():
            log.info("Source directory is empty")
            return

        imageName = self.galleryManager.getCurrentFilename()
        if not imageName:
            log.warning("There is no gallery currently opened.")
            self.updateStatusBarLabel(f"There is no gallery currently opened.")
            return
        src = str(self.galleryManager.getSourcePath())
        dst = str(src / Path("__DELETED__"))

        if not os.path.exists(dst):
            os.makedirs(dst)

        # Check that image was not removed from outside of an app
        if self.srcImageStillExists(src, imageName) is False:
            self.cleanupMissingImage(imageName)
            return

        # Prevent override of an image in dst, if file with same name exist there.
        if self.srcImageExistsInDst(dst, imageName):
            self.handleExistingImageInDst()
            return

        log.info(f"It is found. Possible to move from {src} into {dst}!")

        # Remove current image from the list of images in src directory
        currentItem = self.galleryManager.getCurrentGalleryItem()
        self.moveImageCommand(src, dst, currentItem)
        self.updateStatusBarLabel(f"File Deleted.")

        self.galleryManager.updateCounterLabelText()

        # Play feedback sound
        # if SettingsDialog.playFeedbackSound(): TODO
        # self.mainWindow.feedbackSound.play()
        self.playSoundSignal.emit("SUCCESS_SOUND")

        # Show new image
        self.galleryManager.updatePreview()

        # Restore clean state of the app
        self.updateAndCleanup()


        # # Prevent override of an image in dst, if file with same name exist there.
        # # Beware, it does not have to be image. It can be any file.
        # # TODO: Ugh - problemy - moveHistory entry + _availableMediaFiles a _movedFiles .....
        # # TODO: Rename all ...Image... to ...File...
        # if self.srcImageExistsInDst(dst, imageName):
        #     # self.handleExistingImageInDst()
        #     log.warning(f"File '{imageName}' already exists in __DELETED__. Moving to trash.")
        #     os.remove(Path(src) / Path(imageName))
        #     # return
        # else:
        #     self.moveImageCommand(src, dst, imageName)
        #
        # log.info(f"It is found. Possible to move from {src} into {dst}!")
        #
        # # Remove current image from the list of images in src directory
        # self.updateStatusBarLabel(f"File {imageName} deleted.")
        #
        # self.galleryManager.updateCounterLabelText()
        #
        # # Show new image
        # self.galleryManager.updatePreview()


    def handleKeyOthers(self, event):
        """
        Appends pressed key into the label in the UI.

        Checks, whether currently pressed key sequence corresponds to some
        existing shortcut.

        If such shortcut exists, it moves the current image into corresponding destination.

        HIT!
        """
        log.debug("handleSortMode: Case _ (other keys)")

        pressedKey = event.text()

        # === Handle the ; and , ===
        # TODO: Maybe create 2 separated methods for those: handleKeyStrednik(), handleKeyCarka().
        # Validation of InstantCopy feature: ',' or ';' can be only the first char in sequence.
        # Otherwise, shortcut could match before user could write the ',' or ';'.
        if len(self.keySeq) > 0 and (pressedKey == self._copyAndMoveChar or pressedKey == self._copyAndStopChar):
            # ',' or ';' can be only used as the first character of the sequence
            self.updateStatusBarLabel(f"Temporal copy characters ',' and ';' can only be the used as the first character.")
            return

        moveToNextImage = False
        instantCopy = False
        if pressedKey == self._copyAndMoveChar or pressedKey == self._copyAndStopChar:
            if self.copyAndMove or self.copyAndStop:
                log.debug(f"CopyAndMove or CopyAndStop is already set to True. RETURN.")
                return
            
            log.info(f"';' or ',' ({pressedKey}) detected in the sequence as the first character.")
            instantCopy = True
            match pressedKey:
                case self._copyAndMoveChar:
                    moveToNextImage = True
                    self.copyAndMove = True
                case self._copyAndStopChar:
                    self.copyAndStop = True

            self.updateKeySequenceLabel()
            # stop processing here. We do not want the ',' or ';' to be appended to self.keySeq variable.
            return
        
        # Continue processing of normal characters
        self.keySeq += pressedKey

        fullShortcut = self.getCleanSequence()

        log.debug(f"self.permanentkeySeq: {self.permanentKeySeq}")
        log.debug(f"self.keySeq: {self.keySeq}")
        log.debug(f"permanentSeq + keySeq: {fullShortcut}")

        # Prevent matching empty key sequence
        if not fullShortcut:
            return

        # self.updateStatusBarLabelSignal.emit(f"Hit but No action. Destination directory is empty or does not exist for this shortcut.")
        if not self.shortcutManager.shortcutExistsAndIsFinal(fullShortcut):
            self.updateKeySequenceLabel()
            self.updateTreeViewSignal.emit(fullShortcut)
            return

        log.info("HIT!")

        if self.galleryManager.isGalleryEmpty():
            log.info("Source directory is empty")
            self.updateAndCleanup()
            return

        imageName = self.galleryManager.getCurrentFilename()
        src = str(self.galleryManager.getSourcePath())
        dst = self.shortcutManager.getDstPathForShortcut(fullShortcut)

        if not self.checkDestinationDirectoryExists(dst):
            self.updateAndCleanup()
            return

        # Check that image was not removed from outside of an app
        if not self.srcImageStillExists(src, imageName):
            self.cleanupMissingImage(imageName)  # image still exists - specific cleanup
            self.updateAndCleanup()
            return

        # Prevent override of an image in dst, if file with same name exist there.
        if self.srcImageExistsInDst(dst, imageName):
            self.handleExistingImageInDst()  # Image already exists in Dst - specific cleanup
            self.updateAndCleanup()
            return

        log.info(f"It is found. Possible to move from {src} into {dst}!")

        # Remove current image from the list of images in src directory
        currentSequence = self.getCleanSequence()
        currentItem = self.galleryManager.getCurrentGalleryItem()
        if not self.copyOnly and not instantCopy and not self.copyAndStop and not self.copyAndMove:
            log.info(f"Move operation will be executed. {self.copyOnly} {self.copyAndMove} {self.copyAndStop} {instantCopy}.")
            self.moveImageCommand(src, dst, currentItem)
            self.updateStatusBarLabel(f"Shortcut '{currentSequence}' is used. File moved to '{dst}'.")
        else:
            log.info(f"Copy operation will be executed. {self.copyOnly} {self.copyAndMove} {self.copyAndStop} {instantCopy}")
            self.copyImageCommand(src, dst, currentItem)
            self.updateStatusBarLabel(f"Shortcut '{currentSequence}' is used. File copied to '{dst}'.")

            # TODO: Should instantCopy override Settings? Yes. Add this info to the Documentation.
            # Options:
            #   - 1. Settings->Gotonext overrides everything else.
            #   - 2. , or ; overrules Settings
            # if SettingsDialog.settingsGetAutoNextAfterCopy() and not self.copyAndStop:
            if (SettingsDialog.settingsGetAutoNextAfterCopy() or moveToNextImage or self.copyAndMove) and not self.copyAndStop:
                self.galleryManager.incrementGalleryIndex()

        log.info(f"History entries: {self._historyManager.len()}")

        self.galleryManager.updateCounterLabelText()

        # Play feedback sound
        # if SettingsDialog.playFeedbackSound(): TODO
        # self.mainWindow.feedbackSound.play()
        self.playSoundSignal.emit("SUCCESS_SOUND")

        # Show new image
        self.galleryManager.updatePreview()

        # Restore clean state of the app
        self.updateAndCleanup()


    @pyqtSlot()
    def undo_last_operation(self):
        log.debug("Undo last operation")

        if self._historyManager.empty():
            log.info(f"History is Empty!")
            self.updateStatusBarLabelSignal.emit(f"Nothing to Undo, history is empty.")
            return

        lastEntry = self._historyManager.getLast()
        imageData = lastEntry.imageData
        imageName = lastEntry.imageData.fileName
        src = str(lastEntry.dstPath)  # Beware, We use src from history as dst for Undo-move operation.
        dst = str(lastEntry.srcPath)
        positionIndex = lastEntry.galleryIndex
        operation = lastEntry.operation

        if not self.checkDestinationDirectoryExists(dst):
            return

        # Check that image was not removed from outside of an app
        # if self.srcImageStillExists(src, imageName) is False:
        #     self.cleanupMissingImage(src, imageName)
        #     #if self.mvHistory:  # TODO: Mozna do cleanupMissingImage, mozna jen tu. Jeste nevim.
        #     #    self.mvHistory.pop()
        #     return

        match operation:
            case Operations.MOVE:
                # Prevent override of an image in dst, if file with same name exist there.
                if self.srcImageExistsInDst(dst, imageName):
                    self.handleExistingImageInDst()
                    return

                shutil.move(src + "/" + imageName, dst + "/" + imageName)
                self.updateStatusBarLabel(f"File moved BACK from: {src}.")

                # return back the image into the list of images
                self.galleryManager.restoreFile(imageData, positionIndex)

                # Update counter label
                self.galleryManager.updateCounterLabelText()

            case Operations.COPY:  # Undo copy operation - just delete the image from dst.
                Path.unlink(src + "/" + imageName)
                self.updateStatusBarLabel(f"File deleted from: {src}.")

        # Remove last record from history
        self._historyManager.pop()

        # Success
        # Play feedback sound
        # if SettingsDialog.playFeedbackSound(): TODO
        # self.mainWindow.feedbackSound.play()
        self.playSoundSignal.emit("SUCCESS_SOUND")

        # Show new image
        self.galleryManager.updatePreview()

        # Restore clean state of the app
        # self.updateAndCleanup()


    def handleSortMode(self, event: QKeyEvent):
        # pressedKey = event.text()
        # Cancel currently started shortcut or escape from the hold partial sequence
        match event.key():
            case Qt.Key_Escape:
                self.handleKeyEscape()

            case Qt.Key_Backspace:
                self.handleKeyBackspace()

            # Sentinel: Hold current shortcut and use it as default for upcoming sequences until escape
            case Qt.Key_Return:  # Key_Return is non-numeric Enter key
                self.handleKeyReturn()

            # Single-time move file
            case Qt.Key_Space:
                self.handleKeySpace()

            # Repeat last move from src to dst of current image.
            case Qt.Key_Period:
                self.handleKeyPeriod()

            case Qt.Key_Delete:
                self.handleKeyDelete()

            case _: # Other keys
                self.handleKeyOthers(event)


    def srcImageStillExists(self, src, imageName) -> bool:
        """
        Check that source Image still exists in Src directory.
        This prevents operations on the Image in case the Image was removed from outside
        of the app (for example directly through file manager).
        """
        # if not imageName or not os.path.exists(src + "/" + imageName): # TODO: if some error ocur, add 'if not imageName and'
        if not os.path.exists(src + "/" + imageName):
            return False
        return True


    def srcImageExistsInDst(self, dst: Path, imageName) -> bool:
        """
        Check, whether the file with the same name does not already exist in the destination directory.
        """

        # log.info(f"image: '{imageName}' !!!")
        # log.info(f"Dst: '{dst}'!!!")
        # if os.path.exists(dst + "/" + imageName):
        if os.path.isfile(dst / Path(imageName)):
            log.info(f"Image {imageName} already exists in the {dst}!!!")
            return True
        return False


    def checkDestinationDirectoryExists(self, dst: Path) -> bool:
        """
        Check, whether destination directory exists.
        If it does NOT, return False.
        """
        if dst is None or dst == "" or os.path.exists(dst) is False:
            log.info(f"ERROR: Destination directory {dst} does not exist.")
            self.updateStatusBarLabel(f"ERROR: Destination directory {dst} does not exist.")
            self.keySeq = ""
            self.updateKeySequenceLabel()
            return False
        return True


    def updateAndCleanup(self):
        """
        General restoration of the clean state of the app.

        Call this after error states, like missing image and such.
        """
        self.copyAndMove = False
        self.copyAndStop = False
        self.keySeq = ""
        # self.permanentKeySeq = ""
        self.updateKeySequenceLabel()
        self.updateTreeViewSignal.emit(self.getCleanSequence())
        self.galleryManager.setFocus(True)  # Return focus to the gallerymanager


    def cleanupMissingImage(self, fileData: GalleryItem):
        """
        If an image is not found (deleted from outside the app), then
        remove it from the images list, update preview...
        """
        self.galleryManager.removeFile(fileData)
        self.galleryManager.updateCounterLabelText()
        self.galleryManager.updatePreview()
        self.updateStatusBarLabel(f"File was not found. Probably was removed outside of the app.")


    def handleExistingImageInDst(self):
        """
        Handles situation, when the file with the same name as source image already exist in the destination.

        Currently, prevent any further operations.

        In the future, maybe add a suffix to the filename.
        """
        # TODO: Maybe Add random suffix number to the filename (and update name in the list!)
        self.updateStatusBarLabel(f"File with that name already exists in the dst directory.")


    def addEntryIntoHistory(self, imageData: GalleryItem, src: Path, dst: Path, currentIndex: int, operation: Operations):
        # TODO: maybe ? Replace with the Command and UndoStack.
        newHistoryEntry = HistoryEntry(
            imageData = imageData,
            srcPath = src,
            dstPath = dst,
            galleryIndex = currentIndex,
            operation = operation
        )
        
        # Append entry / Push entry to historyStack
        self._historyManager.push(newHistoryEntry)
        
        # Check:
        print(self._historyManager.top())

    def moveImageCommand(self, src: str|Path, dst: str|Path, imageData: GalleryItem):
        # TODO: Replace with the Command and UndoStack.
        shutil.move(Path(src) / Path(imageData.fileName), Path(dst) / Path(imageData.fileName))
        self.addEntryIntoHistory(imageData, src, dst, self.galleryManager.getGalleryIndex(), Operations.MOVE)
        self.galleryManager.removeFile(imageData)

    def copyImageCommand(self, src: str|Path, dst: str|Path, imageData: GalleryItem):
        # TODO: Replace with the Command and UndoStack.
        shutil.copy2(Path(src) / Path(imageData.fileName), Path(dst) / Path(imageData.fileName))
        self.addEntryIntoHistory(imageData, src, dst, self.galleryManager.getGalleryIndex(), Operations.COPY)

    def afterMoveOperations(self):
        pass


    def beforeMoveOperations(self):
        # 1. space (one-time dst select)
        #     a. open dialog with dst dir from current keySeq, if any
        #     b. check adviced/selected dst dir exists
        #     c. check image was not removed from outside the app
        #     d. check dst does not contain image with same name
        #     e. Move/Copy image from src to dst
        #     f. Remove file from gallery list, if move
        #     g. Append to history
        #     h. Update status bar
        #     i. Clear keySeq
        #     j. Update keySeq label
        #     k. Update counter label
        #     l. Show new image

        # TODO: Udelat funkci nejakou jako zjistitDstDir - esi z dialogu, z historie, z parent's dstdir...
        #        - tam budou veci, jako esi ta dst existuje a pod.
        #        - zavolat ji v pouziti space, pouziti period a v normalni dstdir ze shortcut a undo.
        pass

    def setCopyOnly(self):
        self.copyOnly = True

    def unsetCopyOnly(self):
        self.copyOnly = False

    def isCopyOnly(self) -> bool:
        return self.copyOnly
