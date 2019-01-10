import argparse
import asyncio
import logging
import os
import sys
from contextlib import closing
from functools import partial, partialmethod
from math import floor
from typing import Dict, List, Optional

# noinspection PyUnresolvedReferences
from PyQt5.QtCore import Qt, QThread, pyqtSignal
# noinspection PyUnresolvedReferences
from PyQt5.QtGui import QIcon, QFont, QDropEvent
# noinspection PyUnresolvedReferences
from PyQt5.QtWidgets import QWidget, QListWidget, QAbstractItemView, QLabel, QVBoxLayout, QProgressBar, \
    QListWidgetItem, QMainWindow, QApplication, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QTreeWidget, \
    QTreeWidgetItem, QHeaderView, QHBoxLayout, QPushButton, QLineEdit, QAction
from tkinter import *
import tkinter as tk

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow

class TorrentAddingDialog(QDialog):
    SELECTION_LABEL_FORMAT = 'Selected {} files({})'

    def _traverse_file_tree(self, name: str, node: FileTreeNode, parent: QWidget):
        item = QTreeWidgetItem(parent)
        item.setCheckState(0, Qt.Checked)
        item.setText(0, name)
        if(isinstance(node,
