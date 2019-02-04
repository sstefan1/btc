# BitTorrent Client

## BitTorrent protocol:

* BitTorrent is a peer to peer (P2P) protocol, for sharing files.
* It is based on passing messages directly between peers.

## Bencoding:
* Bencoding is a way to specify and organize data in a terse format. It supports the following types: byte strings, integers, lists, and dictionaries.
- example: d3:cow3:moo4:spam4:eggse represents the dictionary { "cow" => "moo", "spam" => "eggs" } 

## Metainfo file structure:
* All data in a metainfo file is bencoded. The content of a metainfo file (the file ending in ".torrent") is a bencoded dictionary, containing at least keys listed below.
- announce url
- info dictionary

## Peer wire protocol
* Messages:
```
0 - choke
1 - unchoke
2 - interested
3 - not interested
4 - have
5 - bitfield
6 - request
7 - piece
8 - cancel
```
* Besides those, there is one more important message, namely Handshake messake. Handshake is exactly 68 bytes long and consists of <pstrlen><pstr><reserved><info_hash><peer_id>

    <pstrlen> -> always 19, 1 byte
    <pstr> -> b"BitTorrent protocol
    <reserved> -> 8 reserved bytes. For our purposes always 0.
    <info_hash> -> 20 byte SHA1 hash value of 'info' key.
    <peer_id> -> 20 byte string representing unique ID.

## Tracker protocol:
* Tracker is a simple HTTP server that keeps 'track' of the state of the swarm.
* As a response tracker sends compact byte string which contains all tuples of peer's ip and port.

* Example tracker http request:
    - /unnounce?info_hash={}&peer_id={}&port={}&uploaded={}&downloaded={}&left={}&event={}&compact=1
