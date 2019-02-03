import sys
import os
import bencode

from functools import partial, partialmethod
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon, QFont, QDropEvent
from typing import Dict, List, Optional
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from PyQt5.QtWidgets import QWidget, QListWidget, QAbstractItemView, QLabel, QVBoxLayout, QProgressBar, \
    QListWidgetItem, QMainWindow, QApplication, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QTreeWidget, \
    QTreeWidgetItem, QHeaderView, QHBoxLayout, QPushButton, QLineEdit, QAction

from torrent import TrackerInfo, TorrentInfo, Peer, utils
import multiprocessing as mp

from math import floor, log



class TorrentCreatingDialog(QDialog):
    SELECTION_LABEL_FORMAT = 'Selected {} files ({})'

    def _get_directory_browse_widget(self, path):
        widget = QWidget()
        hbox = QHBoxLayout(widget)
        hbox.setContentsMargins(0, 0, 0, 0)

        self._path_edit = QLineEdit(self)
        self._path_edit.setReadOnly(True)
        self._path_edit.setText(path)
        hbox.addWidget(self._path_edit, 4)

        browse_button = QPushButton('Browse...')
        browse_button.clicked.connect(self._browse)
        hbox.addWidget(browse_button, 1)

        widget.setLayout(hbox)
        return widget

    def _browse(self):
        new_download_dir = QFileDialog.getExistingDirectory(self, 'Select download directory', self.path)
        if not new_download_dir:
            return

        self._download_dir = new_download_dir
        self._path_edit.setText(new_download_dir)

    def __init__(self, parent: QWidget, path):
        super().__init__(parent)
        # download_info = torrent_info.download_info
        vbox = QVBoxLayout(self)

        vbox.addWidget(QLabel('Path to file:'))
        vbox.addWidget(self._get_directory_browse_widget(path))

        vbox.addWidget(QLabel('Tracker:'))
        self._tracker_edit = QLineEdit(self)
        self._tracker_edit.setReadOnly(False)
        vbox.addWidget(self._tracker_edit, 4)

        self._button_box = QDialogButtonBox(self)
        self._button_box.setOrientation(Qt.Horizontal)
        self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.submit_torrent)
        self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        vbox.addWidget(self._button_box)

        # self.setFixedSize(250, 200)
        self.setWindowTitle('Create torrent')
        self.path = path

    def _set_check_state_to_tree(self, item: QTreeWidgetItem, check_state: Qt.CheckState):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, check_state)
            self._set_check_state_to_tree(child, check_state)

    def _update_checkboxes(self, item: QTreeWidgetItem, column: int):
        if column != 0:
            return

        new_check_state = item.checkState(0)
        self._set_check_state_to_tree(item, new_check_state)

        while True:
            item = item.parent()
            if item is None:
                break

            has_checked_children = False
            has_partially_checked_children = False
            has_unchecked_children = False
            for i in range(item.childCount()):
                state = item.child(i).checkState(0)
                if state == Qt.Checked:
                    has_checked_children = True
                elif state == Qt.PartiallyChecked:
                    has_partially_checked_children = True
                else:
                    has_unchecked_children = True

            if not has_partially_checked_children and not has_unchecked_children:
                new_state = Qt.Checked
            elif has_checked_children or has_partially_checked_children:
                new_state = Qt.PartiallyChecked
            else:
                new_state = Qt.Unchecked
            item.setCheckState(0, new_state)

        self._update_selection_label()

    def _update_selection_label(self):
        selected_file_count = 0
        selected_size = 0
        for node, item in self._file_items:
            if item.checkState(0) == Qt.Checked:
                selected_file_count += 1
                selected_size += node.length

        ok_button = self._button_box.button(QDialogButtonBox.Ok)
        if not selected_file_count:
            ok_button.setEnabled(False)
            self._selection_label.setText('Nothing to download')
        else:
            ok_button.setEnabled(True)
            # self._selection_label.setText(TorrentAddingDialog.SELECTION_LABEL_FORMAT.format(
                # selected_file_count, humanize_size(selected_size)))

    def submit_torrent(self):
        path = self._path_edit.text()
        utils.create_torrent(self._tracker_edit.text(), path)

        self.close()


class TorrentAddingDialog(QDialog):
    SELECTION_LABEL_FORMAT = 'Selected {} files ({})'

    def _get_directory_browse_widget(self):
        widget = QWidget()
        hbox = QHBoxLayout(widget)
        hbox.setContentsMargins(0, 0, 0, 0)

        self._path_edit = QLineEdit(self.download_path)
        self._path_edit.setReadOnly(False)
        hbox.addWidget(self._path_edit, 4)

        browse_button = QPushButton('Browse...')
        browse_button.clicked.connect(self._browse)
        hbox.addWidget(browse_button, 1)

        widget.setLayout(hbox)
        return widget

    def _browse(self):
        new_download_dir = QFileDialog.getExistingDirectory(self, 'Select download directory', self._torrent_info.file.path)
        if not new_download_dir:
            return

        self.download_path = new_download_dir
        self._path_edit.setText(new_download_dir)
        self.torrent_path = new_download_dir

    def __init__(self, parent: QWidget, torrent_info: TorrentInfo):
        super().__init__(parent)
        self.parent = parent

        self._torrent_info = torrent_info
        self.download_path = torrent_info.download_dir

        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel('Download directory:'))
        vbox.addWidget(self._get_directory_browse_widget())

        self._button_box = QDialogButtonBox(self)
        self._button_box.setOrientation(Qt.Horizontal)
        self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        vbox.addWidget(self._button_box)

        self.torrent_path = torrent_info.name

        self.setFixedSize(500, 200)
        self.setWindowTitle('Adding "{}"'.format(self.torrent_path))

    def _set_check_state_to_tree(self, item: QTreeWidgetItem, check_state: Qt.CheckState):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, check_state)
            self._set_check_state_to_tree(child, check_state)

    def _update_checkboxes(self, item: QTreeWidgetItem, column: int):
        if column != 0:
            return

        new_check_state = item.checkState(0)
        self._set_check_state_to_tree(item, new_check_state)

        while True:
            item = item.parent()
            if item is None:
                break

            has_checked_children = False
            has_partially_checked_children = False
            has_unchecked_children = False
            for i in range(item.childCount()):
                state = item.child(i).checkState(0)
                if state == Qt.Checked:
                    has_checked_children = True
                elif state == Qt.PartiallyChecked:
                    has_partially_checked_children = True
                else:
                    has_unchecked_children = True

            if not has_partially_checked_children and not has_unchecked_children:
                new_state = Qt.Checked
            elif has_checked_children or has_partially_checked_children:
                new_state = Qt.PartiallyChecked
            else:
                new_state = Qt.Unchecked
            item.setCheckState(0, new_state)

        self._update_selection_label()

    def _update_selection_label(self):
        selected_file_count = 0
        selected_size = 0
        for node, item in self._file_items:
            if item.checkState(0) == Qt.Checked:
                selected_file_count += 1
                selected_size += node.length

        ok_button = self._button_box.button(QDialogButtonBox.Ok)
        if not selected_file_count:
            ok_button.setEnabled(False)
            self._selection_label.setText('Nothing to download')
        else:
            ok_button.setEnabled(True)
            # self._selection_label.setText(TorrentAddingDialog.SELECTION_LABEL_FORMAT.format(
                # selected_file_count, humanize_size(selected_size)))

    @staticmethod
    def submit_torrent(parent: QWidget, torrent_info: TorrentInfo):
        dialog = TorrentAddingDialog(parent, torrent_info)
        result = dialog.exec_()
        download_path = dialog.download_path
        return download_path, result == QDialog.Accepted
