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
# noinspection PyUnresolvedReferfrom tkinter import *
# import tkinter as tkences
from PyQt5.QtGui import QIcon, QFont, QDropEvent
# noinspection PyUnresolvedReferences
from PyQt5.QtWidgets import QWidget, QListWidget, QAbstractItemView, QLabel, QVBoxLayout, QProgressBar, \
    QListWidgetItem, QMainWindow, QApplication, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QTreeWidget, \
    QTreeWidgetItem, QHeaderView, QHBoxLayout, QPushButton, QLineEdit, QAction
from tkinter import *
import tkinter as tk
from threading import Thread
import multiprocessing as mp
import time
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow



class Example(QWidget):
    def __init__(self, q: mp.Queue):
        super().__init__()
        self.queue = q
        self.initUI()

    def initUI(self):

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        self.btn = QPushButton('Start', self)
        self.btn.move(40, 80)
        self.btn.clicked.connect(self.doAction)

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('QProgressBar Queue')
        self.show()

    def listen(self):
        while True:
            num = self.queue.get()
            print("got {0}".format(num))
            self.pbar.setValue(num)
            if num == 100:
                break

    def doAction(self):
        self.queue.put('go') # indicate start
        # start thread which listens on the child_connection
        t = Thread(target=self.listen)
        t.start()


def runner(q: mp.Queue):
    go = q.get() # wait for start
    for i in range(101):
        q.put(i)
        print("put {0}".format(i))
        time.sleep(0.1)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 file dialogs - pythonspot.com'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.openFileNameDialog()
        # self.openFileNamesDialog()
        # self.saveFileDialog()

        self.show()


    def openFileNameDialog(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "All Files (*);;Python Files (*.py)", options=options)
        if filename:
            print(filename)

    def openFileNamesDialog(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        if files:

            print(files)

    def saveFileDialog(self):
        options = QFileDialog.Options()

        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.txt)", options=options)
        if filename:
            print(filename)


def a():
    app = QApplication(sys.argv)
    ex = App()
    # sys.exit(app.exec_())


def b():
    # ap = QApplication(sys.argv)
    q = mp.Queue()
    e = Example(q)
    process = mp.Process(target=runner, args=[q])
    process.start()
    # sys.exit(ap.exec_())
# class TorrentAddingDialog(QDialog):
#     SELECTION_LABEL_FORMAT = 'Selected {} files({})'
#
#     def _traverse_file_tree(self, name: str, node: FileTreeNode, parent: QWidget):
#         item = QTreeWidgetItem(parent)
#         item.setCheckState(0, Qt.Checked)
#         item.setText(0, name)
#         if(isinstance(node,

#odvade
root = tk.Tk()
root.title("TorrentCLient")

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
# photo = QIcon(os.path.join("C://Users//mspet//btc//gui//add.svg"))

photo = tk.PhotoImage("C://Users//mspet//btc//gui//add.pgm")
# myImage = Image.open("C:/Users/mspet/Desktop/bit-torrent-master/icons/remove.svg")
# a = tk.Button(root, text="Add", fg="red", image=photo, width="35", height="23", command=a)
a = tk.Button(root, image=photo, command=a)
a.config(width="35", height="23")
a.pack(side=LEFT, anchor=NW)

b = tk.Button(root, text="Pause", fg="white", command=b, bg="black")
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


		