import requests
import bencode
import struct
import socket
from enum import Enum
from datetime import timedelta, datetime
from socket import ntohs

#  TODO: document...ENUM...
class TrackerEvent(Enum):
    STARTED = 0
    PAUSED = 1
    STOPPED = 2


def tracker_event_string(value):
    if value == 0:
        return "started"
    if value == 1:
        return "paused"
    if value == 2:
        return "stopped"


#  Holds info about tracker. Makes requests.
#  Stores its address, and received responses.
class Tracker:
    def __init__(self, address):
        self.address = address
        self.peers = []
        #  datetime of last peer request.
        self.lastPeerRequest = None

        #  Peer request frequency. This wil be timedelta object
        self.peerRequestInterval = None

    def handle_response(self, response):
        if response.status_code != 200:
            return

        be_response = bencode.decode(response.content)
        if be_response is None:
            return

        self.peerRequestInterval = timedelta(seconds=be_response['interval'])
        peer_info = be_response['peers']

        for i in range(len(peer_info) // 6):
            offset = i * 6
            # Format: ! -> treats numbers with network byte order (big endian)
            # Format: 4s <=> ssss -> bytes
            # format: H -> integer (ctype -- unsigned short)
            ip, port = struct.unpack('!4sH', peer_info[offset:offset + 6])
            ip_address = socket.inet_ntoa(ip)
            #  ip_address = str(peer_info[offset]) + '.' + str(peer_info[offset + 1]) + '.' + str(peer_info[offset + 2]) + '.' + str(peer_info[offset + 3])
            #  port = ntohs(int(peer_info[offset + 4:offset + 6]))
            self.peers.append((ip_address, port))

    def update(self, torrent, event, peerid, port):
        # this check will be performed later.
        # if event == TrackerEvent.STARTED and datetime.now() < self.lastPeerRequest + self.peerRequestInterval:
            # return

        self.lastPeerRequest = datetime.now()
        url_string = "{}?info_hash={}&peer_id={}&port={}&uploaded={}&downloaded={}&left={}&event={}&compact=1"
        url = url_string.format(self.address, torrent.safeUrl,
                                str(peerid), port, torrent.uploaded,
                                torrent.downloaded, torrent.file.size,
                                tracker_event_string(event))

        url_hardcoded_1 = "http://192.168.1.9:6969/announce?info_hash=%9E%D5%B1%A6%CD%5E%CB%F21%AAv%C0P%D2%1F!%813%12%CC&peer_id=01234567890123456789&port=6881&uploaded=0&downloaded=0&left=5257556&compact=1&event=started"
        response = requests.get(url)
        self.handle_response(response)
