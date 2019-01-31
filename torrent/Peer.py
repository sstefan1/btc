import socket, select, errno
from torrent import protocol
from torrent import PieceManager


class Peer:
    def __init__(self, torrent, host, port, peer_id):
        self.torrent = torrent
        self.piece_manager = PieceManager.PieceManager(torrent)

        #  ip address.
        # self.host = host
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
        self.chocked = True
        # self.interested = False
        self.peer_socket = None
        self.peers_sockets = {}   # peer dictionary. key=ID, value=Socket

    def send_handshake(self):
        """
        Sends Hendshake message. Since peer should immediately respond
        with his own handshake message, response is recieved from the
        same method.
        """
        peers = self.torrent.tracker.peers

        # for p in peers:
        #     p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #     p_socket.connect((p[0], p[1]))

        #  construct the handshake message
        name_length = bytes([19])
        protocol_name = b'BitTorrent protocol'
        reserved_flags = b'\0' * 8

        info_hash = self.torrent.urlInfoHash
        peer_id = self.peer_id

        handshake_msg = name_length + protocol_name + reserved_flags + info_hash + peer_id

        # Send handshakes to all the peers.
        for p in peers:
            if p[1] == 5555:
                continue
            p_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                p_socket.connect((p[0], p[1]))
                p_socket.send(handshake_msg)
            except:
                continue
            response = p_socket.recv(68)
            if response:
                remote_id = response[48:]
                self.peers_sockets[remote_id] = p_socket
                # self.piece_manager.peers[remote_id]

        # self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # # peer_socket.setblocking(True)
        # #  hardcoded port, discovered via wireshark
        # #  for now, tracker returns wrong port.
        # self.peer_socket.connect((peer[0], peer[1]))
        # self.peer_socket.send(handshake_msg)
        #
        # #  handshake msg is exactly 68 bytes long
        # response = self.peer_socket.recv(68)
        # if len(response) != 68:
        #     return
        #
        # # remote peer_id starts at 48th byte.
        # self.remote_id = response[48:]

        # print(response)

        # Immediately send interested message. Expect unchoke.

        # Get have messages from all the remaining peers.
        # Discard those which are not seeders.
        for p_id, p_sock in self.peers_sockets.items():
            data = self.socket_recv(protocol.REQUEST_SIZE, p_sock)
            while data:
                message = protocol.decode_no_payload(data)
                m_type = message[1]
                length = message[0]

                if m_type == protocol.PeerMessage.BitField:
                    bitfield, _ = protocol.decode_bitfield(data)
                    self.piece_manager.add_peer(p_id, bitfield)
                elif m_type == protocol.PeerMessage.Have:
                    index = protocol.decode_have(data)
                    self.piece_manager.update_peer(p_id, index)

                data = data[4 + length:]

            bitfield = self.piece_manager.peers[p_id]
            if all(b == 1 for b in bitfield):
                continue
            else:
                pass
                # Not seeder. Discard.
                # del self.peers_sockets[p_id]

            # Start downloading
        self.download()

    def download(self):
        self.send_interested()
        self.set_nonblocking()

        request_piece = True
        data = b''
        i = 0
        while True:
            if self.chocked:
                # self.send_interested()
                sockets = self.dict_to_list(self.peers_sockets)
                ready_to_read, ready_to_write, in_error = \
                    select.select(sockets, sockets, sockets)

                if ready_to_read:
                    for s in ready_to_read:
                        data += s.recv(5)  # Unchoke length

                    self.chocked = False
                else:
                    continue
            if request_piece and len(data) < protocol.REQUEST_SIZE:
                sockets = self.dict_to_list(self.peers_sockets)
                # Test request.
                self._request_piece(sockets[i])
                if i < len(sockets) - 1:
                    i += 1

                # data = self.peer_socket.recv(2**14)
                ready_to_read, ready_to_write, in_error = \
                    select.select(sockets, [], [])

                j = 0
                if ready_to_read:
                    for s in ready_to_read:
                        #print(j)
                        #j += 1
                        data += s.recv(protocol.REQUEST_SIZE)
                else:
                    continue

                # data = self.socket_recv(protocol.REQUEST_SIZE)

            if data:
                message = protocol.decode_no_payload(data)

                if message[0] == 0:
                    # KeepAlive received
                    # consume message and continue
                    data = data[4:]
                    continue

                message_type = message[1]

                # if message_type == protocol.PeerMessage.Piece and message[0] > len(data):
                if message_type == protocol.PeerMessage.Piece and ((message[0] > len(data)) or (message[0] < len(data) and message[0] + 4 < len(data))):
                    """ actually any message can have incomplete message."""
                    # Piece messege not complete. Recieve remaining data
                    # data += self.peer_socket.recv(message[0] - len(data) + 4)
                    sockets = self.dict_to_list(self.peers_sockets)
                    ready_to_read, ready_to_write, in_error = \
                        select.select(sockets, [], [])

                    if ready_to_read:
                        for s in ready_to_read:
                            data += s.recv(protocol.REQUEST_SIZE)
                    else:
                        continue
                    # data += self.socket_recv(message[0] - len(data) + 4)

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
                    if len(data) < message[0] + 4:
                        continue
                    piece_message = protocol.decode_piece(data)
                    # self.my_state.remove('pending_request')
                    self.piece_manager.block_received(peer_id=self.remote_id,
                                                      piece_index=piece_message[2],
                                                      block_offset=piece_message[3],
                                                      data=piece_message[4])
                    # print("\t\tRECEIVED BLOCK")
                    request_piece = True
                elif message_type == protocol.PeerMessage.Request:
                    pass
                elif message_type == protocol.PeerMessage.Cancel:
                    pass

                data = data[4 + message[0]:]
                # if not data:
                #     request_piece = True
                # if len(self.piece_manager.missing_pieces) == 0:
                    # return

    def _request_piece(self, p_sock):
        # if 'choked' not in self.my_state and 'interested' in self.my_state and pending
        block = self.piece_manager.next_request()
        if block:
            message = protocol.encode_request(block.piece, block.offset, block.length)
            # self.peer_socket.send(message)
            self.socket_send(p_sock, message)

    def send_interested(self):
        """ Sends interested message to all the peers."""
        interested_msg = protocol.encode_interested()
        # self.peer_socket.send(interested_msg)
        for _, s in self.peers_sockets.items():
            self.socket_send(s, interested_msg)

    def socket_send(self, p_socket, data):
        try:
            p_socket.send(data)
        except socket.error as e:
            print(e)
            peers = self.torrent.tracker.peers
            peer = peers[1]
            self.peer_socket.close()
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_socket.connect((peer[0], peer[1]))

    def socket_recv(self, len, peer_socket):
        try:
            return peer_socket.recv(len);
        except socket.error as e:
            print(e)
            peers = self.torrent.tracker.peers
            peer = peers[1]
            self.peer_socket.close()
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.peer_socket.connect((peer[0], peer[1]))

    def set_nonblocking(self):
        for _, s in self.peers_sockets.items():
            s.setblocking(0)

    def dict_to_list(self, dict):
        list = []
        for key, value in dict.items():
            list.append(value)

        return list
