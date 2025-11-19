import pathlib
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QTreeWidget,
    QTreeWidgetItem
)

from src.ShortcutManager import ShortcutManager
from src.SettingsDialog import SettingsDialog

class CustomTreeWidget(QTreeWidget):

    def __init__(self, shortcut_manager):
        super().__init__()
        self.shortcutManager = shortcut_manager


    @pyqtSlot()
    def update_tree_view(self, root: str = ""):
        # Just flush the whole content of the treeViewWidget and rebuild it from scratch.
        self.clear()
        items = []
        shortcuts_data = self.shortcutManager.getData()  # Original

        # shortcuts_data = self.shortcutManager.getLastKeyParent(root)            # V1
        # shortcuts_data = self.shortcutManager.getLastKeyContentOfSequence(root)  # V2
        # # shortcuts_data = shortcuts_data["keys"]
        #
        # print("Shortcuts_data:", shortcuts_data)
        # print("shortcuts_data2:", self.shortcutManager.getLastKeyContentOfSequence(root))

        # TODO: Do not show subtrees except the one starting with the first pressed key.
        # if root is not None and key_L1 != root:
        #     continue

        maxLevel = SettingsDialog.settingsGetNestingLevels()

        def buildTreeView(parent_key_char: QTreeWidgetItem, itemsInLevel, currentLevel):
            # No more keys under current level exist
            if not itemsInLevel:
                return None
            for key_char, properties in itemsInLevel:
                # last level to be shown (leaf items)
                if currentLevel < maxLevel:
                    dst_path = properties["dst_path"]
                    current_key_char_tree_item = QTreeWidgetItem([key_char, pathlib.Path(dst_path).name])
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
        if not SettingsDialog.settingsGetSortShortcuts():
            nextItems = shortcuts_data["keys"].items()  # Do not sort - insert order
        else:
            nextItems = sorted(shortcuts_data["keys"].items(), key=lambda x: str.casefold(x[0]))  # Sort alphabetically (case insensitive)
            # Show just pressed-key's subtree:
            # if shortcuts_data:
            #     print("Shortcuts_data3:", shortcuts_data)
            #     nextItems = sorted(shortcuts_data["keys"].items(), key=lambda x: str.casefold(x[0]))  # Sort alphabetically (case insensitive)
            # nextitems = sorted(shortcuts_data["keys"].items()), 0)  # Sort alphabetically (case sensitive)

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

