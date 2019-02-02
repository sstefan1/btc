from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget

import multiprocessing as mp

"""
This thread will send a signal to the main thread
once the progress updates. Then the main thread will
update the progress. Previous solution updated the progress
directly from the progress thread which caused the access 
violations.
"""
class UpdaterThread(QThread):

    progress_update = pyqtSignal(int)

    def __init__(self, queue: mp.Queue, file_size):
        self.queue = queue
        self.file_size = file_size
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        num = 0
        while True:
            num += self.queue.get()
            print('gpt {0}'.format(num))
            progress = (num / self.file_size) * 100
            self.progress_update.emit(progress)
            if num == 100:
                return
