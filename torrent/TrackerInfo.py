import requests
import bencode
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

        be_response = bencode.decode(response.text)
        if be_response is None:
            return

        self.peerRequestInterval = timedelta(seconds=be_response['interval'])
        peer_info = be_response['peers']

        for i in range(len(peer_info)):
            offset = i * 6
            ip_address = peer_info[offset] + '.' + peer_info[offset + 1] + '.' + peer_info[offset + 2] + '.' + peer_info[offset + 3]
            port = ntohs(peer_info[offset + 4])
            self.peers.append((ip_address, port))

    def update(self, torrent, event, peerid, port):
        if event == TrackerEvent.STARTET and datetime.now() < self.lastPeerRequest + self.peerRequestInterval:
            return

        self.lastPeerRequest = datetime.now()
        url_string = "{}?info_hash={}&peer_id={}&port={}&uploaded={}&downloaded={}&left={}&event={}&compact=1"
        url = url_string.format(self.address, torrent.urlInfoHash,
                                peerid, port, torrent.uploaded,
                                torrent.downloaded, torrent.left,
                                tracker_event_string(event))

        response = requests.get(url)
        self.handle_response(response)
