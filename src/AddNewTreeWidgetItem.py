from PyQt5.QtWidgets import QTreeWidgetItem


class AddNewTreeWidgetItem(QTreeWidgetItem):
    """
    tree item representing "Add Item" button under current parent's item.
    """

    def __init(self):
        super().__init__()