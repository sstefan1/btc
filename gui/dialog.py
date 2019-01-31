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

from torrent import TrackerInfo, TorrentInfo
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
        # self._torrent_info.download_dir = self._download_dir
        # self._control.last_download_dir = os.path.abspath(self._download_dir)
        #
        # file_paths = []
        # for node, item in self._file_items:
        #     if item.checkState(0) == Qt.Checked:
        #         file_paths.append(node.path)
        # if not self._torrent_info.download_info.single_file_mode:
        #     self._torrent_info.download_info.select_files(file_paths, 'whitelist')
        #
        # self._control_thread.loop.call_soon_threadsafe(self._control.add, self._torrent_info)
        #

        self.close()
        pass


class TorrentAddingDialog(QDialog):
    SELECTION_LABEL_FORMAT = 'Selected {} files ({})'

    def _get_directory_browse_widget(self):
        widget = QWidget()
        hbox = QHBoxLayout(widget)
        hbox.setContentsMargins(0, 0, 0, 0)

        self._path_edit = QLineEdit(self._torrent_info.file.path)
        self._path_edit.setReadOnly(True)
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

        self._download_dir = new_download_dir
        self._path_edit.setText(new_download_dir)

    def __init__(self, parent: QWidget, filename: str, torrent_info: TorrentInfo):
        super().__init__(parent)
        self.parent = parent
        #parent.torrent_added.emit(torrent_info)
        self._torrent_info = torrent_info
        # download_info = torrent_info.download_info
        vbox = QVBoxLayout(self)
        vbox.addWidget(QLabel('Download directory:'))
        vbox.addWidget(self._get_directory_browse_widget())

        self._button_box = QDialogButtonBox(self)
        self._button_box.setOrientation(Qt.Horizontal)
        self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.submit_torrent)
        self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
        vbox.addWidget(self._button_box)

        self.setFixedSize(400, 100)
        self.setWindowTitle('Adding "{}"'.format(filename))

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
        """
        self._torrent_info.download_dir = self._download_dir
        self._control.last_download_dir = os.path.abspath(self._download_dir)

        file_paths = []
        for node, item in self._file_items:
            if item.checkState(0) == Qt.Checked:
                file_paths.append(node.path)
        if not self._torrent_info.download_info.single_file_mode:
            self._torrent_info.download_info.select_files(file_paths, 'whitelist')

        self._control_thread.loop.call_soon_threadsafe(self._control.add, self._torrent_info)

        self.close()
        pass
        """
        self.parent.torrent_added.emit(self._torrent_info)
        self.close()