import os
from math import ceil


class FileInfo:
    def __init__(self, path):
        self.path = path
        self.size = os.path.getsize(path)
        self.offset = None


class Torrent:
    def __init__(self, name, location, file_path, tracker, piece_size, piece_hashes, block_size=16384):
        self.name = name
        self.download_dir = location
        self.file = FileInfo(file_path)

        if tracker is not None:
            self.tracker = tracker

        self.piece_size = piece_size
        self.block_size = block_size

        self.piece_count = ceil(self.file.size / piece_size)
        self.piece_hashes = piece_hashes

        # list of length piece_size.
        self.piece_verified = None

        # Matrix of dimensions [piece_size][piece_size / block_size]
        self.block_verified = None