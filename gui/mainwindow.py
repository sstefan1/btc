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

# <<<<<<< HEAD
# =======
from gui import dialog

# >>>>>>> ae28bc8d43a96238f88d05f74e403dcb1fba7c84
from math import floor, log

from torrent import TorrentInfo, TrackerInfo

ICON_DIRECTORY = os.path.join(os.path.dirname(__file__), 'icons')


def load_icon(name: str):
    return QIcon(os.path.join(ICON_DIRECTORY, name + '.svg'))


file_icon = load_icon('file')
directory_icon = load_icon('directory')


def get_directory(directory: Optional[str]):
    return directory if directory is not None else os.getcwd()


# <<<<<<< HEAD
# class TorrentCreatingDialog(QDialog):
#     SELECTION_LABEL_FORMAT = 'Selected {} files ({})'
#
#     def _get_directory_browse_widget(self):
#         widget = QWidget()
#         hbox = QHBoxLayout(widget)
#         hbox.setContentsMargins(0, 0, 0, 0)
#
#         self._path_edit = QLineEdit(self)
#         self._path_edit.setReadOnly(True)
#         hbox.addWidget(self._path_edit, 4)
#
#         browse_button = QPushButton('Browse...')
#         browse_button.clicked.connect(self._browse)
#         hbox.addWidget(browse_button, 1)
#
#         widget.setLayout(hbox)
#         return widget
#
#     def _browse(self):
#         new_download_dir = QFileDialog.getExistingDirectory(self, 'Select download directory', self.path)
#         if not new_download_dir:
#             return
#
#         self._download_dir = new_download_dir
#         self._path_edit.setText(new_download_dir)
#
#     def __init__(self, parent: QWidget, path):
#         super().__init__(parent)
#         # download_info = torrent_info.download_info
#         vbox = QVBoxLayout(self)
#
#
#         vbox.addWidget(QLabel('Path to file:'))
#         vbox.addWidget(self._get_directory_browse_widget())
#
#         vbox.addWidget(QLabel('Tracker:'))
#         self._path_edit = QLineEdit(self)
#         self._path_edit.setReadOnly(False)
#         vbox.addWidget(self._path_edit, 4)
#
#         self._button_box = QDialogButtonBox(self)
#         self._button_box.setOrientation(Qt.Horizontal)
#         self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
#         self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.submit_torrent)
#         self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
#         vbox.addWidget(self._button_box)
#
#         self.setFixedSize(450, 550)
#         self.setWindowTitle('Create torrent')
#         self.path = path
#
#     def _set_check_state_to_tree(self, item: QTreeWidgetItem, check_state: Qt.CheckState):
#         for i in range(item.childCount()):
#             child = item.child(i)
#             child.setCheckState(0, check_state)
#             self._set_check_state_to_tree(child, check_state)
#
#     def _update_checkboxes(self, item: QTreeWidgetItem, column: int):
#         if column != 0:
#             return
#
#         new_check_state = item.checkState(0)
#         self._set_check_state_to_tree(item, new_check_state)
#
#         while True:
#             item = item.parent()
#             if item is None:
#                 break
#
#             has_checked_children = False
#             has_partially_checked_children = False
#             has_unchecked_children = False
#             for i in range(item.childCount()):
#                 state = item.child(i).checkState(0)
#                 if state == Qt.Checked:
#                     has_checked_children = True
#                 elif state == Qt.PartiallyChecked:
#                     has_partially_checked_children = True
#                 else:
#                     has_unchecked_children = True
#
#             if not has_partially_checked_children and not has_unchecked_children:
#                 new_state = Qt.Checked
#             elif has_checked_children or has_partially_checked_children:
#                 new_state = Qt.PartiallyChecked
#             else:
#                 new_state = Qt.Unchecked
#             item.setCheckState(0, new_state)
#
#         self._update_selection_label()
#
#     def _update_selection_label(self):
#         selected_file_count = 0
#         selected_size = 0
#         for node, item in self._file_items:
#             if item.checkState(0) == Qt.Checked:
#                 selected_file_count += 1
#                 selected_size += node.length
#
#         ok_button = self._button_box.button(QDialogButtonBox.Ok)
#         if not selected_file_count:
#             ok_button.setEnabled(False)
#             self._selection_label.setText('Nothing to download')
#         else:
#             ok_button.setEnabled(True)
#             # self._selection_label.setText(TorrentAddingDialog.SELECTION_LABEL_FORMAT.format(
#                 # selected_file_count, humanize_size(selected_size)))
#
#     def submit_torrent(self):
#         # self._torrent_info.download_dir = self._download_dir
#         # self._control.last_download_dir = os.path.abspath(self._download_dir)
#         #
#         # file_paths = []
#         # for node, item in self._file_items:
#         #     if item.checkState(0) == Qt.Checked:
#         #         file_paths.append(node.path)
#         # if not self._torrent_info.download_info.single_file_mode:
#         #     self._torrent_info.download_info.select_files(file_paths, 'whitelist')
#         #
#         # self._control_thread.loop.call_soon_threadsafe(self._control.add, self._torrent_info)
#         #
#         self.close()
#         pass
#
#
# class TorrentAddingDialog(QDialog):
#     SELECTION_LABEL_FORMAT = 'Selected {} files ({})'
#
#     def _get_directory_browse_widget(self):
#         widget = QWidget()
#         hbox = QHBoxLayout(widget)
#         hbox.setContentsMargins(0, 0, 0, 0)
#
#         self._path_edit = QLineEdit(self._torrent_info.file.path)
#         self._path_edit.setReadOnly(True)
#         hbox.addWidget(self._path_edit, 4)
#
#         browse_button = QPushButton('Browse...')
#         browse_button.clicked.connect(self._browse)
#         hbox.addWidget(browse_button, 1)
#
#         widget.setLayout(hbox)
#         return widget
#
#     def _browse(self):
#         new_download_dir = QFileDialog.getExistingDirectory(self, 'Select download directory', self._torrent_info.file.path)
#         if not new_download_dir:
#             return
#
#         self._download_dir = new_download_dir
#         self._path_edit.setText(new_download_dir)
#
#     def __init__(self, parent: QWidget, filename: str, torrent_info: TorrentInfo):
#         super().__init__(parent)
#         self.parent = parent
#         #parent.torrent_added.emit(torrent_info)
#         self._torrent_info = torrent_info
#         # download_info = torrent_info.download_info
#         vbox = QVBoxLayout(self)
#         vbox.addWidget(QLabel('Download directory:'))
#         vbox.addWidget(self._get_directory_browse_widget())
#
#         self._button_box = QDialogButtonBox(self)
#         self._button_box.setOrientation(Qt.Horizontal)
#         self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
#         self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.submit_torrent)
#         self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
#         vbox.addWidget(self._button_box)
#
#         self.setFixedSize(450, 550)
#         self.setWindowTitle('Adding "{}"'.format(filename))
#
#     def _set_check_state_to_tree(self, item: QTreeWidgetItem, check_state: Qt.CheckState):
#         for i in range(item.childCount()):
#             child = item.child(i)
#             child.setCheckState(0, check_state)
#             self._set_check_state_to_tree(child, check_state)
#
#     def _update_checkboxes(self, item: QTreeWidgetItem, column: int):
#         if column != 0:
#             return
#
#         new_check_state = item.checkState(0)
#         self._set_check_state_to_tree(item, new_check_state)
#
#         while True:
#             item = item.parent()
#             if item is None:
#                 break
#
#             has_checked_children = False
#             has_partially_checked_children = False
#             has_unchecked_children = False
#             for i in range(item.childCount()):
#                 state = item.child(i).checkState(0)
#                 if state == Qt.Checked:
#                     has_checked_children = True
#                 elif state == Qt.PartiallyChecked:
#                     has_partially_checked_children = True
#                 else:
#                     has_unchecked_children = True
#
#             if not has_partially_checked_children and not has_unchecked_children:
#                 new_state = Qt.Checked
#             elif has_checked_children or has_partially_checked_children:
#                 new_state = Qt.PartiallyChecked
#             else:
#                 new_state = Qt.Unchecked
#             item.setCheckState(0, new_state)
#
#         self._update_selection_label()
#
#     def _update_selection_label(self):
#         selected_file_count = 0
#         selected_size = 0
#         for node, item in self._file_items:
#             if item.checkState(0) == Qt.Checked:
#                 selected_file_count += 1
#                 selected_size += node.length
#
#         ok_button = self._button_box.button(QDialogButtonBox.Ok)
#         if not selected_file_count:
#             ok_button.setEnabled(False)
#             self._selection_label.setText('Nothing to download')
#         else:
#             ok_button.setEnabled(True)
#             # self._selection_label.setText(TorrentAddingDialog.SELECTION_LABEL_FORMAT.format(
#                 # selected_file_count, humanize_size(selected_size)))
#
#     def submit_torrent(self):
#         """
#         self._torrent_info.download_dir = self._download_dir
#         self._control.last_download_dir = os.path.abspath(self._download_dir)
#
#         file_paths = []
#         for node, item in self._file_items:
#             if item.checkState(0) == Qt.Checked:
#                 file_paths.append(node.path)
#         if not self._torrent_info.download_info.single_file_mode:
#             self._torrent_info.download_info.select_files(file_paths, 'whitelist')
#
#         self._control_thread.loop.call_soon_threadsafe(self._control.add, self._torrent_info)
#
#         self.close()
#         pass
#         """
#         self.parent.torrent_added.emit(self._torrent_info)
#         self.close()

# class TorrentCreatingDialog(QDialog):
#     SELECTION_LABEL_FORMAT = 'Selected {} files ({})'
#
#     def _get_directory_browse_widget(self):
#         widget = QWidget()
#         hbox = QHBoxLayout(widget)
#         hbox.setContentsMargins(0, 0, 0, 0)
#
#         self._path_edit = QLineEdit(self)
#         self._path_edit.setReadOnly(True)
#         hbox.addWidget(self._path_edit, 4)
#
#         browse_button = QPushButton('Browse...')
#         browse_button.clicked.connect(self._browse)
#         hbox.addWidget(browse_button, 1)
#
#         widget.setLayout(hbox)
#         return widget
#
#     def _browse(self):
#         new_download_dir = QFileDialog.getExistingDirectory(self, 'Select download directory', self.path)
#         if not new_download_dir:
#             return
#
#         self._download_dir = new_download_dir
#         self._path_edit.setText(new_download_dir)
#
#     def __init__(self, parent: QWidget, path):
#         super().__init__(parent)
#         # download_info = torrent_info.download_info
#         vbox = QVBoxLayout(self)
#
#         vbox.addWidget(QLabel('Path to file:'))
#         vbox.addWidget(self._get_directory_browse_widget())
#
#         vbox.addWidget(QLabel('Tracker:'))
#         self._path_edit = QLineEdit(self)
#         self._path_edit.setReadOnly(False)
#         vbox.addWidget(self._path_edit, 4)
#
#         self._button_box = QDialogButtonBox(self)
#         self._button_box.setOrientation(Qt.Horizontal)
#         self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
#         self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.submit_torrent)
#         self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
#         vbox.addWidget(self._button_box)
#
#         # self.setFixedSize(250, 200)
#         self.setWindowTitle('Create torrent')
#         self.path = path
#
#     def _set_check_state_to_tree(self, item: QTreeWidgetItem, check_state: Qt.CheckState):
#         for i in range(item.childCount()):
#             child = item.child(i)
#             child.setCheckState(0, check_state)
#             self._set_check_state_to_tree(child, check_state)
#
#     def _update_checkboxes(self, item: QTreeWidgetItem, column: int):
#         if column != 0:
#             return
#
#         new_check_state = item.checkState(0)
#         self._set_check_state_to_tree(item, new_check_state)
#
#         while True:
#             item = item.parent()
#             if item is None:
#                 break
#
#             has_checked_children = False
#             has_partially_checked_children = False
#             has_unchecked_children = False
#             for i in range(item.childCount()):
#                 state = item.child(i).checkState(0)
#                 if state == Qt.Checked:
#                     has_checked_children = True
#                 elif state == Qt.PartiallyChecked:
#                     has_partially_checked_children = True
#                 else:
#                     has_unchecked_children = True
#
#             if not has_partially_checked_children and not has_unchecked_children:
#                 new_state = Qt.Checked
#             elif has_checked_children or has_partially_checked_children:
#                 new_state = Qt.PartiallyChecked
#             else:
#                 new_state = Qt.Unchecked
#             item.setCheckState(0, new_state)
#
#         self._update_selection_label()
#
#     def _update_selection_label(self):
#         selected_file_count = 0
#         selected_size = 0
#         for node, item in self._file_items:
#             if item.checkState(0) == Qt.Checked:
#                 selected_file_count += 1
#                 selected_size += node.length
#
#         ok_button = self._button_box.button(QDialogButtonBox.Ok)
#         if not selected_file_count:
#             ok_button.setEnabled(False)
#             self._selection_label.setText('Nothing to download')
#         else:
#             ok_button.setEnabled(True)
#             # self._selection_label.setText(TorrentAddingDialog.SELECTION_LABEL_FORMAT.format(
#                 # selected_file_count, humanize_size(selected_size)))
#
#     def submit_torrent(self):
#         # self._torrent_info.download_dir = self._download_dir
#         # self._control.last_download_dir = os.path.abspath(self._download_dir)
#         #
#         # file_paths = []
#         # for node, item in self._file_items:
#         #     if item.checkState(0) == Qt.Checked:
#         #         file_paths.append(node.path)
#         # if not self._torrent_info.download_info.single_file_mode:
#         #     self._torrent_info.download_info.select_files(file_paths, 'whitelist')
#         #
#         # self._control_thread.loop.call_soon_threadsafe(self._control.add, self._torrent_info)
#         #
#         # self.close()
#         pass
#
#
# class TorrentAddingDialog(QDialog):
#     SELECTION_LABEL_FORMAT = 'Selected {} files ({})'
#
#     def _get_directory_browse_widget(self):
#         widget = QWidget()
#         hbox = QHBoxLayout(widget)
#         hbox.setContentsMargins(0, 0, 0, 0)
#
#         self._path_edit = QLineEdit(self._torrent_info.file.path)
#         self._path_edit.setReadOnly(True)
#         hbox.addWidget(self._path_edit, 4)
#
#         browse_button = QPushButton('Browse...')
#         browse_button.clicked.connect(self._browse)
#         hbox.addWidget(browse_button, 1)
#
#         widget.setLayout(hbox)
#         return widget
#
#     def _browse(self):
#         new_download_dir = QFileDialog.getExistingDirectory(self, 'Select download directory', self._torrent_info.file.path)
#         if not new_download_dir:
#             return
#
#         self._download_dir = new_download_dir
#         self._path_edit.setText(new_download_dir)
#
#     def __init__(self, parent: QWidget, filename: str, torrent_info: TorrentInfo):
#         super().__init__(parent)
#         self.parent = parent
#         #parent.torrent_added.emit(torrent_info)
#         self._torrent_info = torrent_info
#         # download_info = torrent_info.download_info
#         vbox = QVBoxLayout(self)
#         vbox.addWidget(QLabel('Download directory:'))
#         vbox.addWidget(self._get_directory_browse_widget())
#
#         self._button_box = QDialogButtonBox(self)
#         self._button_box.setOrientation(Qt.Horizontal)
#         self._button_box.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
#         self._button_box.button(QDialogButtonBox.Ok).clicked.connect(self.submit_torrent)
#         self._button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.close)
#         vbox.addWidget(self._button_box)
#
#         self.setFixedSize(400, 100)
#         self.setWindowTitle('Adding "{}"'.format(filename))
#
#     def _set_check_state_to_tree(self, item: QTreeWidgetItem, check_state: Qt.CheckState):
#         for i in range(item.childCount()):
#             child = item.child(i)
#             child.setCheckState(0, check_state)
#             self._set_check_state_to_tree(child, check_state)
#
#     def _update_checkboxes(self, item: QTreeWidgetItem, column: int):
#         if column != 0:
#             return
#
#         new_check_state = item.checkState(0)
#         self._set_check_state_to_tree(item, new_check_state)
#
#         while True:
#             item = item.parent()
#             if item is None:
#                 break
#
#             has_checked_children = False
#             has_partially_checked_children = False
#             has_unchecked_children = False
#             for i in range(item.childCount()):
#                 state = item.child(i).checkState(0)
#                 if state == Qt.Checked:
#                     has_checked_children = True
#                 elif state == Qt.PartiallyChecked:
#                     has_partially_checked_children = True
#                 else:
#                     has_unchecked_children = True
#
#             if not has_partially_checked_children and not has_unchecked_children:
#                 new_state = Qt.Checked
#             elif has_checked_children or has_partially_checked_children:
#                 new_state = Qt.PartiallyChecked
#             else:
#                 new_state = Qt.Unchecked
#             item.setCheckState(0, new_state)
#
#         self._update_selection_label()
#
#     def _update_selection_label(self):
#         selected_file_count = 0
#         selected_size = 0
#         for node, item in self._file_items:
#             if item.checkState(0) == Qt.Checked:
#                 selected_file_count += 1
#                 selected_size += node.length
#
#         ok_button = self._button_box.button(QDialogButtonBox.Ok)
#         if not selected_file_count:
#             ok_button.setEnabled(False)
#             self._selection_label.setText('Nothing to download')
#         else:
#             ok_button.setEnabled(True)
#             # self._selection_label.setText(TorrentAddingDialog.SELECTION_LABEL_FORMAT.format(
#                 # selected_file_count, humanize_size(selected_size)))
#
#     def submit_torrent(self):
#         """
#         self._torrent_info.download_dir = self._download_dir
#         self._control.last_download_dir = os.path.abspath(self._download_dir)
#
#         file_paths = []
#         for node, item in self._file_items:
#             if item.checkState(0) == Qt.Checked:
#                 file_paths.append(node.path)
#         if not self._torrent_info.download_info.single_file_mode:
#             self._torrent_info.download_info.select_files(file_paths, 'whitelist')
#
#         self._control_thread.loop.call_soon_threadsafe(self._control.add, self._torrent_info)
#
#         self.close()
#         pass
#         """
#         self.parent.torrent_added.emit(self._torrent_info)
#         self.close()


UNIT_BASE = 2 ** 10
UNIT_PREFIXES = 'KMG'


def humanize_size(size: float) -> str:
    if not size:
        return 'None'
    if size < UNIT_BASE:
        return '{:.0f} bytes'.format(size)
    unit = floor(log(size, UNIT_BASE))
    unit_name = UNIT_PREFIXES[min(unit, len(UNIT_PREFIXES)) - 1] + 'iB'
    return '{:.1f} {}'.format(size / UNIT_BASE ** unit, unit_name)


class TorrentListWidget(QListWidget):
    files_dropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.setAcceptDrops(True)

    def drag_handler(self, event: QDropEvent, drop: bool=False):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()

            if drop:
                self.files_dropped.emit([url.toLocalFile() for url in event.mimeData().urls()])
        else:
            event.ignore()

    dragEnterEvent = drag_handler
    dragMoveEvent = drag_handler
    dropEvent = partialmethod(drag_handler, drop=True)


class TorrentListWidgetItem(QWidget):
    _name_font = QFont()
    _name_font.setBold(True)

    _stats_font = QFont()
    _stats_font.setPointSize(10)

    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout(self)
        # self.setMaximumHeight(100)

        self._name_label = QLabel()
        self._name_label.setFont(TorrentListWidgetItem._name_font)
        vbox.addWidget(self._name_label)
        self._name_label.setText("First Torrent")

        self.upper_status_label = QLabel()
        self.upper_status_label.setFont(TorrentListWidgetItem._stats_font)
        vbox.addWidget(self.upper_status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setMaximum(100)
        vbox.addWidget(self.progress_bar)
        self.progress_bar.setValue(50)

        self.lower_status_label = QLabel()
        self.lower_status_label.setFont(TorrentListWidgetItem._stats_font)
        vbox.addWidget(self.lower_status_label)

        self._state = None
        self._waiting_control_action = False

    def set_name(self, name):
        self._name_label.setText(name)

    def set_lower_status(self, status):
        self.lower_status_label.setText(status)

    def set_upper_status(self, status):
        self.upper_status_label.setText(status)

    def set_progress(self, progress):
        self.progress_bar.setValue(progress)


class Example(QMainWindow):
    torrent_added = pyqtSignal(TorrentInfo.Torrent)
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        textEdit = QTextEdit()
        self.setCentralWidget(textEdit)

        exitAct = QAction(QIcon('skull.png'), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exitAct)
        self._add_action = toolbar.addAction(load_icon('add'), 'Open')
        self._add_action.triggered.connect(self._add_torrents_triggered)

        self._add_action = toolbar.addAction(load_icon('add'), 'Create')
        self._add_action.triggered.connect(self._create_torrents_triggered)

        self._pause_action = toolbar.addAction(load_icon('pause'), 'Pause')
        self._pause_action.setEnabled(False)
        self._pause_action.triggered.connect(partial(self._control_action_triggered))

        self._resume_action = toolbar.addAction(load_icon('resume'), 'Resume')
        self._resume_action.setEnabled(False)
        self._resume_action.triggered.connect(partial(self._control_action_triggered))

        self._remove_action = toolbar.addAction(load_icon('remove'), 'Remove')
        self._remove_action.setEnabled(False)
        self._remove_action.triggered.connect(partial(self._control_action_triggered))

        self._about_action = toolbar.addAction(load_icon('about'), 'About')
        self._about_action.triggered.connect(self._show_about)

        self._list_widget = TorrentListWidget()
        self._list_widget.itemSelectionChanged.connect(self._update_control_action_state)
        #  self._list_widget.files_dropped.connect(self.add_torrent_files)
        self.torrent_added.connect(self._add_torrent_item)
        self._torrent_to_item = {}  # type: Dict[bytes, QListWidgetItem]

        self.setCentralWidget(self._list_widget)

        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('Main window')
        self.show()

    def _add_torrent_item(self, torrent_info):
        # torrent_info parameter will be used later.
        widget = TorrentListWidgetItem()
        widget.set_name("FIRST TORRENT")
        widget.set_progress(50)
        widget.set_lower_status("LOWER STATUS")

        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())

        self._list_widget.addItem(item)
        self._list_widget.setItemWidget(item, widget)

    def _control_action_triggered(self, action):
        for item in self._list_widget.selectedItems():
            widget = self._list_widget.itemWidget(item)
            if widget.waiting_control_action:
                continue

            info_hash = item.data(Qt.UserRole)
            widget.waiting_control_action = True

        self._update_control_action_state()

    def _add_torrents_triggered(self):
        paths, _ = QFileDialog.getOpenFileName(self, 'Add torrents', '','Torrent file (*.torrent)')
        self.add_torrent_files(paths)

    def _create_torrents_triggered(self):
        paths, _ = QFileDialog.getOpenFileName(self, 'Add file', '','All files (*)')
        self.create_torrent_files(paths)

    def _show_about(self):
        pass

    # Ovo je kopirano iz benocde-test.py, 45 linija
    # Verovatno ce ovde i ostati.
    def parse_torrent_file(self, file):
        with open(file, 'rb') as f:
            data = f.read()
            be_data = bencode.decode(data)
            return be_data

    def add_torrent_files(self, path):
        # posto je paths samo string, a ne lista stringova kao u resenom
        # ovde ova for petlja ide slovo po slovo, a ne putanju po putanju.
        # for path in paths:
        try:
            tmp = path.split('.')
            # download se vrvt nece koristiti ali za sad ga stavljam da ne bi bacao exception u
            # TorrentInfo.Torrent(...) konstruktoru u 320. liniji.
            download_path = tmp[0] + '.' + tmp[1]
            b_dict = self.parse_torrent_file(path)
            tracker = TrackerInfo.Tracker(b_dict['announce'])
            info = b_dict['info']

            # drugi i treci parametar za sad nek ostanu prazni stringovi
            # to su sada neke putanje, ali mi se ne svidja kako sam za sad to uradio.
            download_path = 'C:/Users/mspet/Desktop/bit-torrent-master/samples/debian-8.3.0-i386-netinst.iso'
            torrent_info = TorrentInfo.Torrent(info, '', download_path, tracker)

            dialog.TorrentAddingDialog(self, tmp, torrent_info).exec()

            # ovu proveru cemo sami uraditi
            # if torrent_info.download_info.info_hash in self._torrent_to_item:
                # raise ValueError('This torrent is already added')
        except Exception as err:
            # tvoja klasa nema polje self._error_happened
            # self._error_happened('Failed to add "{}"'.format(paths), err)
            pass

    def create_torrent_files(self, path):
        dialog.TorrentCreatingDialog(self, path).exec()
        # TorrentCreatingDialog(self).exec()

    def _update_control_action_state(self):
        self._pause_action.setEnabled(False)
        self._resume_action.setEnabled(False)
        self._remove_action.setEnabled(False)
        for item in self._list_widget.selectedItems():
            widget = self._list_widget.itemWidget(item)
            if widget.waiting_control_action:
                continue

            if widget.state.paused:
                self._resume_action.setEnabled(True)
            else:
                self._pause_action.setEnabled(True)
            self._remove_action.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
