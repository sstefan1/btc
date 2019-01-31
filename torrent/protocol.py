import struct
import bitstring


class PeerMessage:
    """
    A message between two peers.

    All of the remaining messages in the protocol take the form of:
        <length prefix><message ID><payload>

    - The length prefix is a four byte big-endian value.
    - The message ID is a single decimal byte.
    - The payload is message dependent.

    NOTE: The Handshake message is different in layout compared to the other
          messages.

    Read more:
        https://wiki.theory.org/BitTorrentSpecification#Messages

    BitTorrent uses Big-Endian (Network Byte Order) for all messages, this is
    declared as the first character being '>' in all pack / unpack calls to the
    Python's `struct` module.
    """
    Choke = 0
    Unchoke = 1
    Interested = 2
    NotInterested = 3
    Have = 4
    BitField = 5
    Request = 6
    Piece = 7
    Cancel = 8
    Port = 9
    KeepAlive = None
    # Handshake and KeepAlive messages have no ID


REQUEST_SIZE = 2**14  # Block size


def decode_no_payload(data):
    # This decodes KeepAlive message. No ID and no payload.
    if len(data) == 4:
        return struct.unpack('>I', data)
    return struct.unpack('>Ib', data[:5])


def encode_keep_alive():
    pass


def encode_choke():
    # '>Ib' format string: BigEndian 4-byte unsigned integer, 1-byte character
    return struct.pack('>Ib',
                       1,   # Message length
                       PeerMessage.Interested)


def encode_unchoke():
    return struct.pack('>Ib',
                       1,   # Message length
                       PeerMessage.Unchoke)


def encode_interested():
    return struct.pack('>Ib',
                       1,  # Message length
                       PeerMessage.Interested)


def encode_not_interested():
    return struct.pack('>Ib',
                       1,   # Message length
                       PeerMessage.Interested)


def encode_bitfield(data):
    bitfield = bitstring.BitArray(bytes=data)
    bits_length = len(bitfield)
    return struct.pack('>Ib' + str(bits_length) + 's',
                       1 + bits_length,  # Message length
                       PeerMessage.BitField,
                       bitfield)     # Payload


def decode_bitfield(data):
    message_length = struct.unpack('>I', data[:4])[0]
    parts = struct.unpack('>Ib' + str(message_length - 1) + 's', data[:4+message_length])
    # remove bitfield message from recv buffer.
    # data = data[4+message_length:]

    return parts[2], data[4+message_length:]


def encode_request(index, begin, length):
    """
    Constructs the Request message.
    The message is used to request a block of a piece.

    The request size for each block is 2^14 bytes, except the final block
    that might be smaller (since not all pieces might be evenly divided by the
    request size).

    :param index: zero based piece index
    :param begin: zero based offset within a piece
    :param length: requested length of data (default 2^14)
    :return: encoded message
    """
    return struct.pack('>IbIII',
                       13,
                       PeerMessage.Request,
                       index,
                       begin,
                       length)


def decode_request(data):
    """
    Decodes request message

    :param data: data to be decoded
    :return: message
    """
    parts = struct.unpack('>IbIII', data)
    return parts


def encode_piece(index, begin, block):
    """
    Constructs the piece message.

    :param index: zero based piece index
    :param begin: zero based offset within a piece
    :param block: block of data
    :return: message
    """

    # piece message length without data is 9.
    message_length = 9 + len(block)
    return struct.pack('>IbII' + str(len(block)) + 's',
                       message_length,
                       PeerMessage.Piece,
                       index,
                       begin,
                       block)


def decode_piece(data):
    """
    decodes the piece message.
    :param data: message
    :return: decoded message

    NOTE: Piece message length without the block data is 9!
    """
    try:
        length = struct.unpack('>I', data[:4])[0]
        parts = struct.unpack('>IbII' + str(length - 9) + 's',  # see NOTE for explanation.
                              data[:length+4])
    except Exception as e:
        print('error in decode_piece')
        return
    return parts


def encode_cancel(index, begin, length):
    """
    Constructs the cancel message.
    Identical to Request, except for ID.

    :param index: zero based piece index
    :param begin: zero based offset within a piece
    :param length: requested length of data
    :return: message
    """

    # piece message length without data is 9.
    return struct.pack('>IbIII',
                       13,
                       PeerMessage.Cancel,
                       index,
                       begin,
                       length)


def decode_cancel(data):
    """
    Decodes the cancel message.

    :param data: message
    :return: decoded message
    """
    parts = struct.unpack('>IbIII', data)
    return parts


def encode_have(index):
    return struct.pack('>IbI',
                       5,   # Message length
                       PeerMessage.Have,
                       index)


def decode_have(data):
    # Have message has fixed length. Length is always 5
    # Plus 4 bytes for size, total size is 9.
    index = struct.unpack('>IbI', data[:9])[2]
    return index
