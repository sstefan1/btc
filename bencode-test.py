import bencode, hashlib, os


def create_torrent(tracker, file):
    be_dict = {'announce': tracker}

    be = bencode.encode(be_dict)
    size = os.path.getsize(file)
    with open(file) as file:
        while True:
            data = file.read()

    torrent_path = file + ".torrent"
    with open(torrent_path, 'a') as torrent_file:
        torrent_file.write(be.decode("utf-8"))


def sha1_file(filepath):
    BUF_SIZE = 65536

    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(r"C:\Users\stefan\Desktop\book.pdf", 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break;
            md5.update(data)
            sha1.update(data)

# print("MD5: {0}".format(md5.hexdigest()))
# print("SHA1: {0}".format(sha1.hexdigest()))
