import shutil
import os
from pathlib import Path
import typing
import logging

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QObject
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QKeyEvent

from src.SettingsDialog import SettingsDialog
from src.Operations import Operations

# TODO: tohle by melo ovlivnovat i edit mode, ne???
allowedKeys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G, Qt.Key_H, Qt.Key_I, Qt.Key_J,
                Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N, Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T,
                Qt.Key_U, Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z]

log = logging.getLogger(__name__)

class SortModeHandler(QObject):
    """
    Handle sort mode of the app.
    Executes operations.
    """

    updateKeySequenceLabelSignal = pyqtSignal(str)
    updateStatusBarLabelSignal = pyqtSignal(str)
    updateTreeViewSignal = pyqtSignal(str)

    def __init__(self, mainWindow, shortcutManager, galleryManager, parent=None):
        super().__init__(parent)
        self.mainWindow = mainWindow
        self.shortcutManager = shortcutManager
        self.galleryManager = galleryManager

        self.keySeqHistory = []
        self.mvHistory = []
        self.keySeq = ""
        self.permanentKeySeq = ""
        self.copyOnly = False
        self.separator = "+"


    def updateKeySequenceLabel(self):
        if self.permanentKeySeq:
            # Sentinel (+) is set.
            self.updateKeySequenceLabelSignal.emit(f"Key Sequence Pressed: \n{self.permanentKeySeq}{self.separator}{self.keySeq}")
        else:
            # No sentinel, just shortcut.
            self.updateKeySequenceLabelSignal.emit(f"Key Sequence Pressed: \n{self.keySeq}")


    def updateStatusBarLabel(self, newStatusbarMessage: str):
        self.updateStatusBarLabelSignal.emit(newStatusbarMessage)


    def handleSortMode(self, event: QKeyEvent):
        pressedKey = event.text()
        # Cancel currently started shortcut or escape from the hold partial sequence
        match event.key():
            case Qt.Key_Escape:
                log.debug("handleSortMode: Case 'Escape'")
                # log.info(f"key_seq: {self.key_seq}")
                # log.info(f"permanent_key_seq: {self.permanent_key_seq}")
                # TODO: Refactor this: pridat flag sentinelExists, bude to srozumitelnejsi.
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
                log.debug("handleSortMode: Case 'Backspace'")
                if len(self.keySeq) >= 1:
                    self.keySeq = self.keySeq[:-1]
                    self.updateKeySequenceLabel()

            # Sentinel: Hold current shortcut and use it as default for upcoming sequences until escape
            case Qt.Key_Return:  # Key_Return is non-numeric Enter key
                log.debug("handleSortMode: Case 'Enter' (Key_Return)")

                if self.keySeq:
                    self.permanentKeySeq = self.keySeq
                    self.keySeq = ""

                self.updateKeySequenceLabel()

            # Single-time move file
            case Qt.Key_Space:
                log.debug("handleSortMode: Case 'Space'")
                log.info("Select destination directory just for the current image.")
                dst = ""

                # TODO: Refactor celou tuhle hruzu::::::
                # If keySeq is empty, pressing "space" will allow user to select dst dir for one-time use.
                # and else dst directory is chosen from the current non-terminal shortcut, if dst_path is not empty.
                if self.keySeq:
                    log.info(f"keySeq is not empty ('{self.keySeq}')")
                    nonTerminalKey = self.shortcutManager.getLastKeyContentOfSequence(self.keySeq)
                    if nonTerminalKey:
                        dst = nonTerminalKey["dst_path"]
                        if not os.path.exists(dst):
                            log.info(f"No action. Shortcut probably does not contain dst_path ({dst}).")
                            self.updateStatusBarLabelSignal.emit(f"No action. Destination directory is empty or does not exist for shortcut ({self.keySeq}).")
                            return
                        log.info(f"middle_path {dst}")
                    else:
                        log.info(f"Shortcut sequence {self.keySeq} does not exist.")
                        return

                else:  # KeySeq is empty
                    singleUseDstDirectory = QFileDialog.getExistingDirectory(self.mainWindow, "Select Directory")

                    # Check that some directory was selected
                    if not singleUseDstDirectory:
                        self.updateStatusBarLabel(f"No directory was selected.")
                        return

                    log.info(singleUseDstDirectory)
                    dst = singleUseDstDirectory

                src = self.galleryManager.getSourcePath()
                imageName = self.galleryManager.getCurrentFilename()

                # Check that image was not removed from outside of an app
                if self.srcImageStillExists(src, imageName) is False:
                    self.cleanupMissingImage(src, imageName)
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if self.srcImageExistsInDst(dst, imageName):

                    self.handleExistingImageInDst()
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
                            "gallery_index": self.galleryManager.getGalleryIndex(),
                            "operation": Operations.MOVE
                        }
                    )
                    self.updateStatusBarLabel(f"File moved to {dst}.")
                else:
                    shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                    self.mvHistory.append(
                            {
                                "src": src,
                                "dst": dst,
                                "image": imageName,
                                "gallery_index": self.galleryManager.getGalleryIndex(),
                                "operation": Operations.COPY
                            }
                        )
                    if SettingsDialog.settingsGetAutoNextAfterCopy():
                        self.galleryManager.decrementGalleryIndex()

                    self.updateStatusBarLabel(f"File copied to {dst}.")

                self.keySeq = ""
                # log.info(f"History entries: {len(self.mvHistory)}")
                self.updateKeySequenceLabel()
                self.galleryManager.updateCounterLabelText()

                # Show new image
                self.galleryManager.updatePreview()

            # Repeat last move from src to dst of current image.
            case Qt.Key_Period:
                log.debug("handleSortMode: Case '.'")
                # TODO: refactor: Mohlo by to vypadat nejak takhle:
                # if history is empty: 
                #     return
                # src = self.mvHistory[-1]["src"]
                # dst = self.mvHistory[-1]["dst"]
                # tryToMoveImage(src, dst, currentImage)
                log.info("Repeat last finished command for current image")

                if len(self.mvHistory) <= 0 or len(self.keySeqHistory) <= 0:
                    log.info("History is empty.")
                    return

                log.info(f"Last history entry: {self.keySeqHistory[-1]}")

                imageName = self.galleryManager.getCurrentFilename()

                src = self.mvHistory[-1]["src"]
                dst = self.mvHistory[-1]["dst"]

                if not self.checkDestinationDirectoryExists(dst):
                    return

                # Check that image was not removed from outside of an app
                if self.srcImageStillExists(src, imageName) is False:
                    self.cleanupMissingImage(src, imageName)
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if self.srcImageExistsInDst(dst, imageName):
                    self.handleExistingImageInDst()
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
                            "gallery_index": self.galleryManager.getGalleryIndex(),
                            "operation": Operations.MOVE
                        }
                    )
                    self.updateStatusBarLabel(f"File moved to {dst}.")
                else:
                    shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                    self.mvHistory.append(
                            {
                                "src": src,
                                "dst": dst,
                                "image": imageName,
                                "gallery_index": self.galleryManager.getGalleryIndex(),
                                "operation": Operations.COPY
                            }
                        )
                    if SettingsDialog.settingsGetAutoNextAfterCopy():
                        self.galleryManager.incrementGalleryIndex()

                    self.updateStatusBarLabel(f"File copied to {dst}.")
                

                log.info(f"History entries: {len(self.mvHistory)}")
                self.galleryManager.updateCounterLabelText()

                # Show new image
                self.galleryManager.updatePreview()


            case Qt.Key_Delete:
                log.debug("handleSortMode: Case 'Delete'")
                if self.galleryManager.isGalleryEmpty():
                    log.info("Source directory is empty")
                    return

                imageName = self.galleryManager.getCurrentFilename()
                src = self.galleryManager.getSourcePath()
                dst = src + "/" + "__DELETED__"

                if not os.path.exists(dst):
                    os.makedirs(dst)

                # Check that image was not removed from outside of an app
                if self.srcImageStillExists(src, imageName) is False:
                    self.cleanupMissingImage(src, imageName)
                    return

                # Prevent override of an image in dst, if file with same name exist there.
                if self.srcImageExistsInDst(dst, imageName):
                    self.handleExistingImageInDst()
                    return

                log.info(f"It is found. Possible to move from {self.galleryManager.getSourcePath()} into {dst}!")

                # Remove current image from the list of images in src directory
                self.galleryManager.removeFile(imageName)
                shutil.move(src + "/" + imageName, dst + "/" + imageName)
                self.mvHistory.append(
                    {
                        "src": src,
                        "dst": dst,
                        "image": imageName,
                        "gallery_index": self.galleryManager.getGalleryIndex(),
                        "operation": Operations.MOVE
                    }
                )
                self.updateStatusBarLabel(f"File Deleted.")

                self.galleryManager.updateCounterLabelText()

                # Show new image
                self.galleryManager.updatePreview()

            case _: # Other keys
                log.debug("handleSortMode: Case _ (other keys)")
                if event.key() not in allowedKeys:
                    log.info("not [a-zA-Z1-9] was pressed, nothing to append to shortcuts.")
                    return

                self.keySeq += pressedKey

                self.updateTreeViewSignal.emit(self.keySeq)

                fullShortcut = ""
                if self.permanentKeySeq:
                    fullShortcut = self.permanentKeySeq + self.keySeq
                else:
                    fullShortcut = self.keySeq

                log.info(f"key_seq: {self.keySeq}")
                log.info(f"full key_seq: {fullShortcut}")

                # log.info(f"dst for shortcut: {self.shortcut_manager.get_dst_for_shortcut(full_shortcut)}")
                if not self.keySeq:
                    return

                # self.updateStatusBarLabelSignal.emit(f"Hit but No action. Destination directory is empty or does not exist for this shortcut.")
                dstPath = self.shortcutManager.getDstPathForShortcut(fullShortcut)
                if dstPath:
                    log.info("HIT!")

                    if self.galleryManager.isGalleryEmpty():
                        log.info("Source directory is empty")
                        self.keySeq = ""
                        self.updateKeySequenceLabel()
                        return

                    imageName = self.galleryManager.getCurrentFilename()
                    src = self.galleryManager.getSourcePath()
                    dst = dstPath

                    if not self.checkDestinationDirectoryExists(dst):
                        return

                    # Check that image was not removed from outside of an app
                    if self.srcImageStillExists(src, imageName) is False:
                        self.cleanupMissingImage(src, imageName)
                        return

                    # Prevent override of an image in dst, if file with same name exist there.
                    if self.srcImageExistsInDst(dst, imageName):
                        self.handleExistingImageInDst()
                        return

                    self.keySeqHistory.append(fullShortcut)

                    log.info(f"It is found. Possible to move from {self.galleryManager.getSourcePath()} into {dst}!")

                    # Remove current image from the list of images in src directory
                    if not self.copyOnly:
                        self.galleryManager.removeFile(imageName)
                        shutil.move(src + "/" + imageName, dst + "/" + imageName)
                        self.mvHistory.append(
                            {
                                "src": src,
                                "dst": dst,
                                "image": imageName,
                                "gallery_index": self.galleryManager.getGalleryIndex(),
                                "operation": Operations.MOVE
                            }
                        )
                        self.updateStatusBarLabel(f"File moved to {dst}.")
                    else:
                        shutil.copy2(src + "/" + imageName, dst + "/" + imageName)
                        self.mvHistory.append(
                            {
                                "src": src,
                                "dst": dst,
                                "image": imageName,
                                "gallery_index": self.galleryManager.getGalleryIndex(),
                                "operation": Operations.COPY
                            }
                        )
                        if SettingsDialog.settingsGetAutoNextAfterCopy():
                            self.galleryManager.incrementGalleryIndex()

                        self.updateStatusBarLabel(f"File copied to {dst}.")

                    log.info(f"History entries: {len(self.mvHistory)}")
                    # Update counter label
                    self.galleryManager.updateCounterLabelText()

                    # Show new image
                    self.galleryManager.updatePreview()

                    # Enable temporaly save and reuse partial shortcut
                    self.keySeq = ""
                    self.updateKeySequenceLabel()
                else:
                    self.updateKeySequenceLabel()

    @pyqtSlot()
    def undo_last_operation(self):
        log.debug("Undo last operation")
        # log.info(self.mv_history)

        if not self.mvHistory:
            log.info(f"History is Empty!")
            self.updateStatusBarLabelSignal.emit(f"Nothing to Undo, history is empty.")
            return

        imageName = self.mvHistory[-1]["image"]
        src = self.mvHistory[-1]["dst"]
        dst = self.mvHistory[-1]["src"]
        positionIndex = self.mvHistory[-1]["gallery_index"]
        operation = self.mvHistory[-1]["operation"]

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
                self.galleryManager.addFile(imageName, positionIndex)

                # Update counter label
                self.galleryManager.updateCounterLabelText()

            case Operations.COPY:  # Undo copy operation - just delete the image from dst.
                Path.unlink(src + "/" + imageName)
                self.updateStatusBarLabel(f"File deleted from: {src}.")

        # Remove last record from history
        if self.mvHistory:
            self.mvHistory.pop()

        # Show new image
        self.galleryManager.updatePreview()
        # log.info(self.images)



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

    def cleanupAndRestartState(self):
        """
        TODO: Vsude se opakuje:
        
        self.keySeq = ""
        self.updateKeySequenceLabel()

        a dalsi, jako:
        
        self.galleryManager.updateCounterLabelText()
        self.galleryManager.updatePreview()
         
        ktere vrati stav do startovni pozice. Uklidi po nacatych operacich.
        Tohle by se melo volat i v pomocnych funkcich, aby se nikde neopakovala ta sama sekvence kodu porad...
        """


    def cleanupMissingImage(self, src, imageName):
        """
        If an image is not found (deleted from outside the app), then
        remove it from the images list, update preview...
        """
        self.galleryManager.removeFile(imageName)
        self.updateStatusBarLabel(f"File was not found. Probably was removed outside of the app.")
        self.galleryManager.updateCounterLabelText()
        self.galleryManager.updatePreview()
        self.keySeq = ""
        self.updateKeySequenceLabel()
        # if self.mvHistory:  # TODO maybe remove? pros / cons
        #     self.mvHistory.pop()


    def srcImageExistsInDst(self, dst, imageName) -> bool:
        """
        Check, whether the file with the same name does not already exist in the destination directory.
        """
        
        # log.info(f"image: '{imageName}' !!!")
        # log.info(f"Dst: '{dst}'!!!")
        # if os.path.exists(dst + "/" + imageName):
        if os.path.isfile(dst + "/" + imageName):
            log.info(f"Image {imageName} already exists in the {dst}!!!")
            return True
        return False


    def handleExistingImageInDst(self):
        """
        Handles situation, when the file with the same name as source image already exist in the destination.

        Currently, prevent any further operations.
        
        In the future, maybe add a suffix to the filename.
        """
        # TODO: Maybe Add random suffix number to the filename (and update name in the list!)
        self.updateStatusBarLabel(f"File with that name already exists in the dst directory.")
        self.keySeq = ""
        self.updateKeySequenceLabel()


    def checkDestinationDirectoryExists(self, dst) -> bool:
        """
        Check, whether destination directory exists.
        If it does NOT, return False.
        """
        if not os.path.exists(dst):
            log.info(f"ERROR: Destination directory {dst} does not exist.")
            self.updateStatusBarLabel(f"ERROR: Destination directory {dst} does not exist.")
            self.keySeq = ""
            self.updateKeySequenceLabel()
            return False
        return True


    
    def moveImageFromTo(self, src, dst):
        pass


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

    def getCopyOnlyState(self) -> bool:
        return self.copyOnly