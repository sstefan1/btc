import bencode
import hashlib
import os

from torrent import  TrackerInfo, TorrentInfo


def create_torrent(tracker, file):
    be_dict = {'announce': tracker}

    name = file.split("\\")[-1]
    size = os.path.getsize(file)

    # Default piece length is 512kB.
    piece_length = (2**9) * 1000
    pieces = sha1_file(file, piece_length)

    # info dictionary.
    info_dict = {'length': size, 'name': name, 'piece_length': piece_length, 'pieces': pieces}
    be_dict['info'] = info_dict

    be = bencode.encode(be_dict)

    torrent_path = file + ".torrent"
    # bencode.bwrite(be, torrent_path)
    with open(torrent_path, 'wb') as torrent_file:
        torrent_file.write(be)


def sha1_file(filepath, BUFF_SIZE):
    result = []
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(BUFF_SIZE)
            if not data:
                break;
            piece_hash = hashlib.sha1(data).digest()
            result.append(piece_hash)

    return b''.join(result)

# with open(r"C:\Users\stefan\Desktop\book.pdf", 'rb') as f:


def parse_torrent_file(file):
    with open(file, 'rb') as f:
        data = f.read()
        be_data = bencode.decode(data)
        return be_data
        # tracker = TrackerInfo()


def main():
    file_path = r"C:\Users\stefan\Desktop\book.pdf"
    create_torrent("192.168.1.10/announce:6192", file_path)
    be_dict = parse_torrent_file(file_path + ".torrent")
    tracker = TrackerInfo.Tracker(be_dict['announce'])
    info = be_dict['info']
    torrent = TorrentInfo.Torrent(info['name'], "N/A", file_path, tracker, info['piece_length'], info['pieces'])
    a = torrent


if __name__ == "__main__":
    main()
