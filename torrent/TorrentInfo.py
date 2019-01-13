import os
import bencode
import codecs
import urllib.parse
from hashlib import sha1
from math import ceil

from btc.torrent import FileInfo


def slash_escape(err):
    """ codec error handler. err is UnicodeDecode instance. Returns
    a tuple with a replacement for the unencodable part of the input
    and position where encoding should continue. """

    the_byte = err.object[err.start:err.end]
    repl = u'\\x' + hex(ord(the_byte))[2:]
    return repl, err.end


codecs.register_error('slash_escape', slash_escape)

#  class FileInfo:
    #  def __init__(self, path):
        #  self.path = path
        #  self.size = os.path.getsize(path)
        #  self.offset = None


class Torrent:
    def __init__(self, info, location, file_path, tracker, block_size=16384):
        self.name = info['name']
        self.download_dir = location
        self.file = FileInfo.FileInfo(file_path)
        self.downloaded = 0
        self.uploaded = 0

        if tracker is not None:
            self.tracker = tracker

        self.piece_size = info['piece length']
        self.block_size = block_size

        self.piece_count = ceil(self.file.size / self.piece_size)

        # string of 20-byte hash values of each piece.
        self.piece_hashes = info['pieces']

        self.urlInfoHash = sha1(bencode.encode(info)).digest()
        self.safeUrl = urllib.parse.quote(self.urlInfoHash)

        # list of length piece_size.
        self.piece_verified = None

        # Matrix of dimensions [piece_size][piece_size / block_size]
        self.block_verified = None

    def update(self, event, peerid, port):
        self.tracker.update(self, event, peerid, port)

