import socket
from torrent import protocol
from torrent import PieceManager


class Peer:
    def __init__(self, torrent, host, port, peer_id):
        self.torrent = torrent
        self.piece_manager = PieceManager.PieceManager(torrent)

        #  ip address.
        self.host = host
        self.port = port

        #  20 byte random value
        self.peer_id = peer_id

        # peer_id of remote peer
        self.remote_id = None

        self.uploaded = 0
        self.downloaded = 0

        self.message = ""

        self.peer_state = []
        self.my_state = []
        # self.chocked = True
        # self.interested = False

    def send_handshake(self):
        """
        Sends Hendshake message. Since peer should immediately respond
        with his own handshake message, response is recieved from the
        same method.
        """
        peers = self.torrent.tracker.peers

        #  this is a tuple.
        peer = peers[1]

        #  construct the handshake message
        name_length = bytes([19])
        protocol_name = b'BitTorrent protocol'
        reserved_flags = b'\0' * 8

        info_hash = self.torrent.urlInfoHash
        peer_id = self.peer_id

        handshake_msg = name_length + protocol_name + reserved_flags + info_hash + peer_id

        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.setblocking(True)
        #  hardcoded port, discovered via wireshark
        #  for now, tracker returns wrong port.
        peer_socket.connect((peer[0], peer[1]))
        peer_socket.send(handshake_msg)

        #  handshake msg is exactly 68 bytes long
        response = peer_socket.recv(68)
        if len(response) != 68:
            return

        # remote peer_id starts at 48th byte.
        self.remote_id = response[48:]

        print(response)

        request_piece = False
        data = None
        while True:
            if not data:
                # Test request.
                if request_piece:
                    piece_msg_req = protocol.encode_piece(1, 2, 3)
                    peer_socket.send(piece_msg_req)
                data = peer_socket.recv(2**14)

            if data:
                message = protocol.decode_no_payload(data)
                if (message[0] == 0) and (message[1] == 0):
                    data = None
                    continue
                message_type = message[1]
                if message_type == protocol.PeerMessage.BitField:
                    # TODO: Handle empty bitfield message. Empty Bitfield message is followed by Have messages for all the pieces peer has.
                    bitfield, _ = protocol.decode_bitfield(data)
                    self.piece_manager.add_peer(self.remote_id, bitfield)
                elif message_type == protocol.PeerMessage.Have:
                    index = protocol.decode_have(data)
                    self.piece_manager.update_peer(self.remote_id, index)
                elif message_type == protocol.PeerMessage.Interested:
                    self.peer_state.append('interested')
                elif message_type == protocol.PeerMessage.NotInterested:
                    if 'interested' in self.peer_state:
                        self.peer_state.remove('interested')
                elif message_type == protocol.PeerMessage.Choke:
                    self.my_state.append('choked')
                elif message_type == protocol.PeerMessage.Unchoke:
                    if 'choked' in self.my_state:
                        self.my_state.remove('choked')
                elif message_type == protocol.PeerMessage.KeepAlive:
                    pass
                elif message_type == protocol.PeerMessage.Piece:
                    piece_message = protocol.decode_piece(data)
                    self.my_state.remove('pending_request')
                    self.piece_manager.block_received(peer_id=self.remote_id,
                                                      piece_index=piece_message[2],
                                                      block_offset=piece_message[3],
                                                      data=piece_message[4])
                elif message_type == protocol.PeerMessage.Request:
                    pass
                elif message_type == protocol.PeerMessage.Cancel:
                    pass

                data = data[4 + message[0]:]
                if not data:
                    request_piece = True
