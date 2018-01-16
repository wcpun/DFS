from rpyc import connect
import logging
from sys import argv, exit
from chunker import Chunker
from crypto import Crypto
from utils import Meta, Code, Cipher
from contextlib import contextmanager

logging.basicConfig(level=logging.DEBUG)

# 1 GB
BYTE_SIZE = 1024 * 1024 * 1024


@contextmanager
def con(ip, port):
    try:
        server = connect(ip, port, config={"allow_public_attrs": True})
        yield server
        server.close()
    except ConnectionError:
        logging.error("Cannot Connect to Server.")
        exit(1)


def put(user_id, fileName):
    # read data from input file
    with open(fileName, 'rb') as fin:
        bytes = fin.read(BYTE_SIZE)
        fileSize = len(bytes)
        logging.debug("Bytes read with length {0}.".format(fileSize))

    # begin chunking
    chunkObj = Chunker()
    cuts = chunkObj.chunking(bytes)
    logging.debug("Num of Cuts: {0}".format(len(cuts)))
    # for index, chunk in enumerate(chunkObj.divide_chunk(bytes, cuts)):
    #     logging.debug("Chunk {0}: {1}".format(index, chunk))
    logging.info("Chunking completed.\n")

    # create meta data
    fid = fileName + str(user_id)
    cryptObj = Crypto(fid, 'client')
    iv = cryptObj.gen_iv(bytes)
    metaObj = Meta(user_id, fileName, fileSize, iv)
    logging.debug("FileName: {0}".format(metaObj.fileName))
    logging.debug("IV: {0}\n".format(iv))

    # gen keys
    try:
        keys = []
        with con("localhost", 18862) as keyserver:
            if keyserver.root.isExist(fid):
                logging.error("File Already Exist.")
                exit(1)
            for i, chunk in enumerate(chunkObj.divide_chunk(bytes, cuts)):
                key = keyserver.root.gen_key(fid, chunk)
                if not key:
                    logging.error("Key is empty.")
                    exit(1)
                keys.append(key)
                logging.debug("Key {0}: {1}".format(i, key))
    except:
        logging.error("Cannot generate key.")
        exit(1)
    logging.info("Key generation completed.\n")

    # encrypt chunks
    ciphers = []
    count = 0
    for chunk, key in zip(chunkObj.divide_chunk(bytes, cuts), keys):
        cipher = cryptObj.encode(chunk, key, iv)
        ciphers.append(cipher)
        # logging.debug("Cipher {0}: {1}".format(count, cipher))
        count += 1
    del bytes
    del keys
    logging.info("Encryption completed.\n")

    # send ciphers to server
    try:
        with con("localhost", 18861) as master:
            if master.root.put(metaObj):
                for cipher in ciphers:
                    master.root.put(metaObj, cipher)
                    logging.info("Chunk with size {0} uploaded.".format(len(cipher)))
            else:
                logging.error("File Already Exist.")
                exit(1)
    except:
        logging.error("Cannot upload file.")
        exit(1)


def get(user_id, fileName):
    metaObj = Meta(user_id, fileName)
    fid = fileName + str(user_id)

    # recv key first
    try:
        with con("localhost", 18862) as keyserver:
            keys = [key for key in keyserver.root.recv_key(fid) if key]
            if not keys:
                logging.error("File Does not Exist.")
                exit(1)
            logging.info("All Key received.\n")
    except:
        logging.error("Cannot recev key.")
        exit(1)

    cryptObj = Crypto(fid, 'client')

    # recv ciphers and decrypt them
    try:
        with con("localhost", 18861) as master:
            for index, (cipher, iv) in enumerate(master.root.get(metaObj)):
                if not cipher:
                    logging.error("File Does not Exist.")
                    break
                # logging.debug("Cipher: {0}".format(cipher))
                logging.debug("Key: {0}".format(keys[index]))
                logging.debug("IV: {0}".format(iv))
                with open(fileName + '.download', "ab") as fout:
                    chunk = cryptObj.decode(cipher, keys[index], iv)
                    fout.write(chunk)
                logging.info("Chunk with size {0} downloaded.\n".format(len(chunk)))
    except:
        logging.error("Cannot download file.")
        exit(1)


def remove(user_id, fileName):
    metaObj = Meta(user_id, fileName)
    fid = fileName + str(user_id)

    # del key first
    try:
        with con("localhost", 18862) as keyserver:
            if not keyserver.root.del_key(fid):
                logging.error("File does not exist.")
                exit(1)
        logging.info("All Key deleted.")
    except:
        logging.error("Cannot delete key.")
        exit(1)

    # del all chunks that compose the file
    try:
        with con("localhost", 18861) as master:
            if not master.root.remove(metaObj):
                logging.error("File does not exist.")
                exit(1)
        logging.info("All chunks deleted.\n")
    except:
        logging.error("Cannot delete file.")
        exit(1)


def usage():
    usage = "\nUsage:" \
            "python client.py [option] <User Id, FileName>\n\n" \
            "Options:\n" \
            "  -u,    upload file\n" \
            "  -d,    download file\n" \
            "  -r,    remove file\n\n" \
            "Examples:\n" \
            "  $ python client.py -u 1 a1.txt\n" \
            "  $ pythoo client.py -d 1 a2.txt"
    print(usage)
    exit(1)


if __name__ == "__main__":
    if len(argv) < 4:
        usage()
    user_id, fileName = argv[2:]
    if argv[1] == "-u":
        put(user_id, fileName)
    if argv[1] == "-d":
        get(user_id, fileName)
    if argv[1] == "-r":
        remove(user_id, fileName)
