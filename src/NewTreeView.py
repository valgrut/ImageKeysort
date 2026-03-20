from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple

from PyQt5.QtCore import (
    Qt, QModelIndex, QAbstractItemModel, QSortFilterProxyModel, QMimeData, QByteArray
)
from PyQt5.QtGui import QBrush, QColor, QPainter
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTreeView, QMenu, QAction, QFileDialog, QInputDialog,
    QStyledItemDelegate, QMainWindow, QApplication
)




class ShortcutsTreeView(QWidget):
    """
    Use like:
        w = ShortcutsTreeView(shortcut_manager)
        layout.addWidget(w)
    """
    def __init__(self, shortcut_manager, parent=None):
        super().__init__(parent)
        self.shortcutManager = shortcut_manager

        self.view = QTreeView()
        self.view.setUniformRowHeights(True)
        self.view.setAlternatingRowColors(True)
        self.view.setSortingEnabled(False)

        self.model = ShortcutTreeModel(self.shortcutManager.getData(), self)
        self.proxy = RecursiveFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy.setRecursiveFilteringEnabled(False)  # we implement recursion ourselves

        self.view.setModel(self.proxy)
        self.view.setItemDelegate(PathItemDelegate(self.view))
        self.view.expandAll()
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self._on_context_menu)

        # drag/drop move
        self.view.setDragEnabled(True)
        self.view.setAcceptDrops(True)
        self.view.setDropIndicatorShown(True)
        self.view.setDefaultDropAction(Qt.MoveAction)
        self.view.setDragDropMode(QTreeView.InternalMove)

        lay = QVBoxLayout(self)
        lay.addWidget(self.view)

    # def reload_from_manager(self):
    def update_tree_view(self):
        self.model.reset_from_dict(self.shortcutManager.getData())
        self.view.expandAll()

    def _on_context_menu(self, pos):
        proxy_index = self.view.indexAt(pos)
        if not proxy_index.isValid():
            return

        src_index = self.proxy.mapToSource(proxy_index)
        node = src_index.internalPointer()

        menu = QMenu(self)

        act_set_path = QAction("Set destination path…", self)
        act_rename_key = QAction("Rename key…", self)
        act_remove = QAction("Remove shortcut", self)

        menu.addAction(act_set_path)
        menu.addAction(act_rename_key)
        menu.addSeparator()
        menu.addAction(act_remove)

        def set_path():
            # choose directory; you can replace with your custom dialog
            start_dir = node.dst_path or str(Path.home())
            dst = QFileDialog.getExistingDirectory(self, "Select destination directory", start_dir)
            if dst:
                self.model.setData(self.model.index(src_index.row(), ShortcutTreeModel.COL_DST, src_index.parent()), dst)

        def rename_key():
            new_key, ok = QInputDialog.getText(self, "Rename key", "New key:", text=node.key)
            if ok and new_key:
                self.model.setData(self.model.index(src_index.row(), ShortcutTreeModel.COL_KEY, src_index.parent()), new_key)

        def remove():
            self.model.removeRows(src_index.row(), 1, src_index.parent())

        act_set_path.triggered.connect(set_path)
        act_rename_key.triggered.connect(rename_key)
        act_remove.triggered.connect(remove)

        menu.exec_(self.view.viewport().mapToGlobal(pos))
