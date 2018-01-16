from rpyc import Service
from rpyc import connect
from rpyc.utils.server import ThreadedServer
import logging
from contextlib import contextmanager
from utils import Meta, Code, Cipher
from dedup import Dedup

logging.basicConfig(level=logging.INFO)


@contextmanager
def con(ip, port):
    try:
        server = connect(ip, port, config={"allow_public_attrs": True})
        yield server
        server.close()
    except ConnectionError:
        logging.error("Cannot Connect to Server.")
        exit(1)


def init_master(dedupObj):
    class Master(Service):
        def on_connect(self):
            pass

        def on_disconnect(self):
            dedupObj.save()
            fileTable = dedupObj.fileMenu['filetable']
            logging.info("Num of file stored: {0}".format(len(fileTable.keys())))
            for index, fid in enumerate(fileTable.keys()):
                chunklist = fileTable[fid]['cid']
                logging.info("Num of chunks of file_{0}: {1}".format(index, len(chunklist)))

        def exposed_put(self, metaObj=None, cipher=None):
            if not cipher:
                return dedupObj.start_first_stage(metaObj)
            if cipher:
                logging.info("PUT: User ID: {0}.".format(metaObj.user_id))
                logging.info("PUT: File Name: {0}".format(metaObj.fileName))
                if dedupObj.start_second_stage(metaObj, cipher):
                    logging.info("PUT: Received Chunk is Unique.\n")
                    chunkName = dedupObj.hash(cipher)
                    with con("localhost", 18863) as slave:
                        slave.root.put(chunkName, cipher)
                else:
                    logging.info("PUT: Received Chunk is not Unique.\n")

        def exposed_get(self, metaObj):
            logging.info("GET: User ID: {0}.".format(metaObj.user_id))
            logging.info("GET: File Name: {0}\n".format(metaObj.fileName))
            with con("localhost", 18863) as slave:
                for cid, iv in dedupObj.restore(metaObj):
                    cipher = slave.root.get(cid)
                    logging.debug("GET: Cipher restored: {0}".format(cipher))
                    logging.debug("GET: IV restored: {0}\n".format(iv))
                    yield cipher, iv

        def exposed_remove(self, metaObj):
            logging.info("REMOVE: User ID: {0}.".format(metaObj.user_id))
            logging.info("REMOVE: File Name: {0}\n".format(metaObj.fileName))
            result = dedupObj.remove(metaObj)
            if isinstance(result, bool) and not result:
                return False
            else:
                with con("localhost", 18863) as slave:
                    for cid in result:
                        slave.root.remove(cid)
                return True

        def exposed_printObj(self, utilObj):
            print(utilObj)

    return Master


def main():
    dedupObj = Dedup()
    master = init_master(dedupObj)
    config = {"allow_public_attrs": True}
    logger = logging.getLogger("{0}/{1}".format("MASTER", "18861"))
    master_thread = ThreadedServer(service=master, port=18861, logger=logger,
                                   protocol_config=config)
    master_thread.start()


if __name__ == "__main__":
    main()
