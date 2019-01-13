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
    # Handshake and KeepAlive messages have no ID
    REQUEST_SIZE = 2**14 # Block size


def decode_no_payload(data):
    return struct.unpack('>Ib', data)


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
    parts = struct.unpack('>Ib' + str(message_length - 1) + 's', data)

    return parts[2]