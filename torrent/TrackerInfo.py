import requests
from enum import Enum
from datetime import timedelta, datetime
from socket import ntohs

#  TODO: document...ENUM...
class TrackerEvent(Enum):
    STARTED = 0
    PAUSED = 1
    STOPPED = 2


def trackerEventString(value):
    if(value == 0):
        return "started"
    if(value == 1):
        return "paused"
    if value == 2:
        return "stopped"


#  Holds info about tracker. Makes requests.
Stores its address, and received responses.
class TrackerInfo:
    def __init__(self, address):
        self.address = address
        self.peers = []
        #  datetime of last peer request.
        self.lastPeerRequest = None

        #  Peer request frequency. This wil be timedelta object
        self.peerRequestInterval = None


    def Update(self, torrent, event, peerId, port):
        if(event == TrackerEvent.STARTET and datetime.now() < lastPeerRequest + peerRequestInterval)
            return

        lastPeerRequest = datetime.now()
        url_string = "{}?info_hash={}&peer_id={}&port={}&uploaded={}&downloaded={}&left={}&event={}&compact=1"
        url = url_string.format(self.address, torrent.urlInfoHash, peerId, port, torrent.uploaded, torrent.downloaded, torrent.left, trackerEventString(event))

        response = request.get(url)


    def handleResponse(response):
        if response.status_code != 200:
            continue

        be_response = bencode.decode(response.text)
        if be_response == None:
            return

        peerRequestInterval = timedelta(seconds=be_response['interval'])
        peer_info = be_response['peers']

        for i in range(len(peer_info)):
            offset = i * 6
            ip_address = peer_info[offset] + '.' + peer_info[offset + 1] + '.' + peer_info[offset + 2] + '.' + peer_info[offset + 3]
            port = ntohs(peeringo[offset + 4])
            peers.append((ip_address, port))



