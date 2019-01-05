from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QFileDialog, QTreeWidget, QTreeWidgetItem


class TorrentAddingDialog(QDialog):
    SELECTION_LABEL_FORMAT = 'Selected {} files({})'

    def _traverse_file_tree(self, name: str, node: FileTreeNode, parent: QWidget):
        item = QTreeWidgetItem(parent)
        item.setCheckState(0, Qt.Checked)
        item.setText(0, name)
        if(isinstance(node,
