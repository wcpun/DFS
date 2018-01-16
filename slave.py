from rpyc import Service
from rpyc.utils.server import ThreadedServer
from contextlib import contextmanager
import logging
import os


logging.basicConfig(level=logging.DEBUG)

BYTE_SIZE = 1024 * 1024 * 1024


class Slave(Service):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def exposed_put(self, chunkName, chunk):
        with open("data/" + chunkName, "wb") as fin:
            fin.write(chunk)
            logging.debug("Chunk with size {0} written.".format(len(chunk)))

    def exposed_get(self, chunkName):
        with open("data/" + chunkName, "rb") as fout:
            chunk = fout.read(BYTE_SIZE)
            logging.debug("Chunk with size {0} read.".format(len(chunk)))
        return chunk

    def exposed_remove(self, chunkName):
        try:
            os.remove("data/" + chunkName)
            logging.debug("Remove chunk {0}.".format(chunkName))
        except OSError:
            logging.error("Cannot remove chunk.")


def main():
    config = {"allow_public_attrs": True}
    logger = logging.getLogger("{0}/{1}".format("SLAVE", "18863"))
    slave_thread = ThreadedServer(service=Slave, port=18863, logger=logger,
                                  protocol_config=config)
    slave_thread.start()


if __name__ == "__main__":
    main()
