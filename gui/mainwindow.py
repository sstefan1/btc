import sys
import os
import multiprocessing as mp

from functools import partial, partialmethod
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon, QFont, QDropEvent
from typing import Dict, Optional
from PyQt5.QtCore import Qt, pyqtSignal

from PyQt5.QtWidgets import QWidget, QListWidget, QAbstractItemView, QLabel, QVBoxLayout, QProgressBar, \
    QListWidgetItem, QMainWindow, QApplication, QFileDialog, QAction

from gui import dialog, UpdaterThread
from math import floor, log
from torrent import TorrentInfo, TrackerInfo, Peer, PieceManager, utils

ICON_DIRECTORY = os.path.join(os.path.dirname(__file__), 'icons')


def load_icon(name: str):
    return QIcon(os.path.join(ICON_DIRECTORY, name + '.svg'))


file_icon = load_icon('file')
directory_icon = load_icon('directory')


def get_directory(directory: Optional[str]):
    return directory if directory is not None else os.getcwd()


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

    def __init__(self, queue: mp.Queue, file_size):
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
        self.updater_thread = UpdaterThread.UpdaterThread(queue=queue, file_size=file_size)
        self.updater_thread.progress_update.connect(self.update_progress)
        vbox.addWidget(self.progress_bar)
        self.progress_bar.setValue(50)

        self.lower_status_label = QLabel()
        self.lower_status_label.setFont(TorrentListWidgetItem._stats_font)

        vbox.addWidget(self.lower_status_label)

        self.num_peers = 0

        self._state = None
        self._waiting_control_action = False

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
        if progress == 100:
            self.lower_status_label.setText('Seeding...')

    def set_name(self, name):
        self._name_label.setText(name)

    def get_name(self):
        return self._name_label.text()

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
        self._remove_action.triggered.connect(partial(self._remove_torrent_item))

        self._about_action = toolbar.addAction(load_icon('about'), 'About')
        self._about_action.triggered.connect(self._show_about)

        self._list_widget = TorrentListWidget()
        self._list_widget.itemSelectionChanged.connect(self._update_control_action_state)
        #  self._list_widget.files_dropped.connect(self.add_torrent_files)
        self.torrent_added.connect(self._add_torrent_item)
        self._torrent_to_item = {}  # type: Dict[bytes, QListWidgetItem]

        # adds name of added torrent.
        self.added_torrents = []

        self.setCentralWidget(self._list_widget)

        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle('Main window')
        self.show()

#    def closeEvent(self, *args, **kwargs):


    def _add_torrent_item(self, torrent_info, seed):
        queue = mp.Queue()
        widget = TorrentListWidgetItem(queue, torrent_info.info['length'])
        widget.set_name(torrent_info.name)
        widget.set_lower_status('Announcing...')
        if seed:
            widget.progress_bar.setValue(100)
            widget.set_lower_status('Seeding...')
        else:
            widget.progress_bar.setValue(0)

        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())

        if len(self.added_torrents) == 0:
            self.added_torrents.append(torrent_info.name)
        else:
            if torrent_info.name in self.added_torrents:
                return
            self.added_torrents.append(torrent_info.name)

        self._list_widget.addItem(item)
        self._list_widget.setItemWidget(item, widget)


        # Announce.
        if seed:
            torrent_info.downloaded = torrent_info.file.size
            torrent_info.update(0, '01234567890123456789', 5555, 0)
        else:
            torrent_info.update(0, '01234567890123456789', 5555, torrent_info.file.size)

        widget.num_peers = len(torrent_info.tracker.peers) - 1
        if not seed:
            widget.lower_status_label.setText('Downloading from ' + str(widget.num_peers) + 'peers')

        peer = Peer.Peer(torrent_info, '192.168.1.10', 5555, b'01234567890123456789')

        process = None
        if seed:
            process = mp.Process(target=peer.start_seeding, args=[None])
        else:
            process = mp.Process(target=peer.send_handshake, args=[queue])
            widget.updater_thread.start()

        # Starts downloader/uploader process.
        process.start()

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

    def _remove_torrent_item(self):
        listItems = self._list_widget.selectedItems()
        if not listItems: return
        for item in listItems:
            name = self._list_widget.itemWidget(item).get_name()
            if name in self.added_torrents:
                self._list_widget.takeItem(self._list_widget.row(item))
                self.added_torrents.remove(name)

        self._update_control_action_state()

    def _show_about(self):
        pass

    def add_torrent_files(self, path):
        try:
            b_dict = utils.parse_torrent_file(path)
            tracker = TrackerInfo.Tracker(b_dict['announce'])
            info = b_dict['info']

            default_path = path.replace(info['name'] + '.torrent', '')
            file_path = path.replace('.torrent', '')

            torrent_info = TorrentInfo.Torrent(info, '', default_path, tracker)

            download_path, ok = dialog.TorrentAddingDialog.submit_torrent(self, torrent_info)
            if ok:
                torrent_info.download_dir = download_path
            else:
                return

            download_path = download_path + info['name']
            piece_length = (2**9) * 1000  # 512kB
            if os.path.exists(download_path):
                result = utils.compare_files(download_path, info['pieces'], piece_length)
            else:
                result = False
            self._update_control_action_state()

            if result:
                # files are identical
                self._add_torrent_item(torrent_info, True)
            else:
                self._add_torrent_item(torrent_info, False)

        except Exception as err:
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

            if self._add_torrents_triggered:
                self._remove_action.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
