import socket
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
        peers = self.tracker.peers

        #  construct the handshake message
        name_length = bytes([19])
        protocol_name = b'BitTorrent protocol'
        reserved_flags = b' ' * 8

        info_hash = self.torrent.urlInfoHash
        peer_id = self.peer_id

        hadnskahe_msg = name_length + protocol_name + info_hash + peer_id

        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((self.host, self.port))
        peer_socket.send(handshake_msg)

        #  handshake msg is exactly 68 bytes long
        response = socket.recv(68)
        print(response)
