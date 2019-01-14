import socket, errno
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
        self.peer_socket = None

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

        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # peer_socket.setblocking(True)
        #  hardcoded port, discovered via wireshark
        #  for now, tracker returns wrong port.
        self.peer_socket.connect((peer[0], peer[1]))
        self.peer_socket.send(handshake_msg)

        #  handshake msg is exactly 68 bytes long
        response = self.peer_socket.recv(68)
        if len(response) != 68:
            return

        # remote peer_id starts at 48th byte.
        self.remote_id = response[48:]

        # print(response)

        # Immediately send interested message. Expect unchoke.
        self.send_interested()

        request_piece = False
        data = None
        while True:
            if not data:
                # Test request.
                if request_piece:
                    self._request_piece()
                # data = self.peer_socket.recv(2**14)
                data = self.socket_recv(protocol.REQUEST_SIZE)

            if data:
                message = protocol.decode_no_payload(data)

                if message[0] == 0:
                    # KeepAlive received
                    # consume message and continue
                    data = data[4:]
                    continue

                message_type = message[1]

                if message_type == protocol.PeerMessage.Piece and message[0] > len(data):
                    # Piece messege not complete. Recieve remaining data
                    # data += self.peer_socket.recv(message[0] - len(data) + 4)
                    data += self.socket_recv(message[0] - len(data) + 4)

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
                    print('CHOKE RECEIVED!!!')
                    self.my_state.append('choked')
                elif message_type == protocol.PeerMessage.Unchoke:
                    if 'choked' in self.my_state:
                        self.my_state.remove('choked')
                elif message_type == protocol.PeerMessage.KeepAlive:
                    pass
                elif message_type == protocol.PeerMessage.Piece:
                    # if len(data) < message[0]:
                    #     # there is not enough data to decode piece message. Receive more data.
                    #     peer_socket.recv(protocol.REQUEST_SIZE)
                    #     continue
                    piece_message = protocol.decode_piece(data)
                    # self.my_state.remove('pending_request')
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

    def _request_piece(self):
        # if 'choked' not in self.my_state and 'interested' in self.my_state and pending
        block = self.piece_manager.next_request(self.remote_id)
        if block:
            message = protocol.encode_request(block.piece, block.offset, block.length)
            # self.peer_socket.send(message)
            self.socket_send(message)

    def send_interested(self):
        interested_msg = protocol.encode_interested()
        # self.peer_socket.send(interested_msg)
        self.socket_send(interested_msg)


    def socket_send(self, data):
        try:
            self.peer_socket.send(data)
        except socket.error as e:
            print(e)
            peers = self.torrent.tracker.peers
            peer = peers[1]
            self.peer_socket.close()
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_socket.connect((peer[0], peer[1]))

    def socket_recv(self, len):
        try:
            return self.peer_socket.recv(len);
        except socket.error as e:
            print(e)
            peers = self.torrent.tracker.peers
            peer = peers[1]
            self.peer_socket.close()
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_socket.connect((peer[0], peer[1]))
