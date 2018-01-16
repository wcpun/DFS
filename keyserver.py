from rpyc import Service
from rpyc.utils.server import ThreadedServer
from keymenu import KeyMenu
from crypto import Crypto
import logging

logging.basicConfig(level=logging.DEBUG)




def init_keyserver(keymenu):
    class KeyServer(Service):
        def on_connect(self):
            pass

        def on_disconnect(self):
            keymenu.save()
            filelist = keymenu.keyMenu['fids']
            keys = keymenu.keyMenu['keys']
            logging.debug("Num of file stored: {0}".format(len(filelist)))
            for index, fid in enumerate(filelist):
                logging.debug("Num of keys of file_{0}: {1}".format(index, len(keys[fid])))

        def exposed_isExist(self, fid):
            return keymenu.isExist(fid)

        def exposed_gen_key(self, fid, chunk):
            cryptObj = Crypto(fid, 'ks')
            key = cryptObj.gen_key(chunk)
            if keymenu.push(fid, key):
                return key
            else:
                return None

        def exposed_recv_key(self, fid):
            for key in keymenu.pop(fid):
                yield key

        def exposed_del_key(self, fid):
            return keymenu.remove(fid)

        def exposed_hi(self):
            print("hello world.")

    return KeyServer


def main():
    keymenu = KeyMenu()
    ks = init_keyserver(keymenu)
    config = {"allow_public_attrs": True}
    logger = logging.getLogger("{0}/{1}".format("KEYSERVER", "18862"))
    ks_thread = ThreadedServer(service=ks, port=18862, logger=logger,
                               protocol_config=config)
    ks_thread.start()


if __name__ == "__main__":
    main()
