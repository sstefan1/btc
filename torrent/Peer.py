
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

