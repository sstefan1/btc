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

#odvade

# Add a grid
mainframe = Frame(root)
mainframe.grid(column=0, row=0)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)
mainframe.pack()


canvas = Canvas(root, bg='white')
canvas.pack(side=BOTTOM, anchor=W)


tkvar = StringVar(root)

# Dictionary with options
choices = {'New', 'Open'}

popupMenu = OptionMenu(root, tkvar, *choices).pack(side=LEFT, anchor=NW)

photo = PhotoImage("C:\\Users\\Mimin\\Desktop\\blok4\\btc-master\\gui\\remove.svg")

a = tk.Button(root, text="Add", fg="red", command=quit)
#a.config(image=photo, width="35", height="23")
a.pack(side=LEFT, anchor=NW)

b = tk.Button(root, text="Pause", fg="red", command=quit)
#b.config(width="1", height="1")
b.pack(side=LEFT, anchor=NW)

c = tk.Button(root, text="Resume", fg="red", command=quit)
#c.config(width="1", height="1")
c.pack(side=LEFT, anchor=NW)

d = tk.Button(root, text="Remove", fg="red", command=quit)
#d.config(width="1", height="1")
d.pack(side=LEFT, anchor=NW)

e = tk.Button(root, text="About", fg="red", command=quit)
#e.config(width="1", height="1")
e.pack(side=LEFT, anchor=NW)

root.mainloop()

		
		