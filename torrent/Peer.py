import socket
import os

class Peer:
    def __init__(self, torrent, host, port, peer_id):
        self.torrent = torrent

        #  ip address.
        self.host = host
        self.port = port

        #  20 byte random value
        self.peer_id = peer_id

        self.uploaded = 0
        self.downloaded = 0

        self.message = ""

    #  send handshake encoded message
    def send_handshake(self):
        #  send handshake to each peer in peer list
        peers = self.tracker.peers
        peer_sockets = []

        #  for p in peers:
        #  construct the handshake message
        name_length = bytes([19])
        protocol_name = b'BitTorrent protocol'
        reserved_flags = b' ' * 8

        info_hash = self.torrent.urlInfoHash
        peer_id = self.peer_id

        hadnskahe_msg = name_length + protocol_name + info_hash + peer_id

        peer_sockets.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((self.host, self.port))
        peer_socket.send(handshake_msg)

        #  handshake msg is exactly 68 bytes long
        response = socket.recv(68)
        print(response)

    def send_block(self, piece, block, socket):
        offset = self.piece_size * piece + self.block_size * block
        with open(self.file.path, 'rb+') as file:
            file.seek(offset)
            to_send = self.block_size
            while to_send > 0
               data = file.read(4086)
               socket.send(data)
               to_send = to_send - 4086
               file.seek(4086, os.SEEK_CUR)


    def recv_block(self, piece, block, sock):
        offset = self.piece_size * piece + self.block_size * block
        with open(self.file.path, 'rb+') as file:

