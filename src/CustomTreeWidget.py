import os
from pathlib import Path
import logging
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem
)
from PyQt5.QtGui import (QColor, QGradient, QLinearGradient, QBrush)

from src.SettingsDialog import SettingsDialog

log = logging.getLogger(__name__)


class CustomTreeWidget(QTreeWidget):

    def __init__(self, shortcut_manager):
        super().__init__()
        self.shortcutManager = shortcut_manager

    @pyqtSlot()
    @pyqtSlot(str)
    def update_tree_view(self, root: str = ""):
        log.debug(f"Shortcut passed from signal: {root}")
        
        # Just flush the whole content of the treeViewWidget and rebuild it from scratch.
        self.clear()
        items = []
        shortcuts_data = self.shortcutManager.getData()  # Original

        if SettingsDialog.settingsGetShowSubtreeOnly() and root:
            shortcuts_data = self.shortcutManager.getLastKeyContentOfSequence(root)

        maxLevel = SettingsDialog.settingsGetNestingLevels()

        def buildTreeView(parent_key_char: QTreeWidgetItem, itemsInLevel, currentLevel):
            # No more keys under current level exist
            if not itemsInLevel:
                return None
            for key_char, properties in itemsInLevel:
                # last level to be shown (leaf items)
                if currentLevel < maxLevel:
                    dst_path = properties["dst_path"]
                    current_key_char_tree_item = QTreeWidgetItem([key_char, Path(dst_path).name])
                    
                    # Highlight non-existing destination paths in the Tree view
                    if dst_path and not os.path.exists(dst_path):
                        # current_key_char_tree_item.setBackground(1, QColor(200, 50, 0))
                        current_key_char_tree_item.setForeground(1, QColor(200, 50, 0))
                        current_key_char_tree_item.setToolTip(1, f"Destination path '{dst_path}' could not be found!")
                    else:
                        current_key_char_tree_item.setToolTip(1, f"{dst_path}")
                    
                    parent_key_char.addChild(current_key_char_tree_item)

                    # Process current key_char's children
                    nextItems = []
                    if not SettingsDialog.settingsGetSortShortcuts():
                        nextItems = properties["keys"].items()  # Do not sort - insert order
                    else:
                        nextItems = sorted(properties["keys"].items(), key=lambda x: str.casefold(x[0]))  # Sort alphabetically (case insensitive)
                        # nextitems = sorted(properties["keys"].items()), 0)  # Sort alphabetically (case sensitive)

                    # buildTreeView(current_key_char_tree_item, properties["keys"].items(), currentLevel + 1)
                    buildTreeView(current_key_char_tree_item, nextItems, currentLevel + 1)


        firstItem = QTreeWidgetItem(["level0"])

        nextItems = []
        if self.shortcutManager.shortcutExists(root):
            if SettingsDialog.settingsGetSortShortcuts():
                nextItems = sorted(shortcuts_data["keys"].items(), key=lambda x: str.casefold(x[0]))  # Sort alphabetically (case insensitive)
            else:
                nextItems = shortcuts_data["keys"].items()  # Do not sort - insert order


        buildTreeView(firstItem, nextItems, 0)

        # newItem = QTreeWidgetItem(["test"])
        # items.append(newItem)

        # Test of custom items with buttons:
        # myWidget = TreeItemWithButtons()
        # self.treeViewWidget.setItemWidget(newItem, 2, myWidget)

        # Retrieve list of children to fill 'items' list
        items = firstItem.takeChildren()
        self.insertTopLevelItems(0, items)
        self.expandAll()
        print(f"Hide first item: ")
        firstItem.setHidden(True)


