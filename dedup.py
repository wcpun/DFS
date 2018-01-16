from utils import Meta, Code, Cipher
import hashlib
import pickle
import os.path
import logging


class Dedup:
    def __init__(self):
        self.pickle = "index.pickle"
        self.fileMenu = dict()
        if not os.path.exists(self.pickle):
            self.fileMenu['filetable'] = dict()
            self.fileMenu['pointertable'] = dict()
        else:
            with open(self.pickle, 'rb') as fin:
                self.fileMenu = pickle.load(fin)

    def start_first_stage(self, metaObj):
        fileTable = self.fileMenu['filetable']
        fid = self.hash(metaObj.fileName + str(metaObj.user_id))
        if fid not in fileTable.keys():
            fileTable[fid] = dict()
            fileTable[fid]['cid'] = []
            fileTable[fid]['iv'] = metaObj.iv
            return True
        return False

    def start_second_stage(self, metaObj, cipher):
        fileTable = self.fileMenu['filetable']
        pointerTable = self.fileMenu['pointertable']
        cid = self.hash(cipher)
        fid = self.hash(metaObj.fileName + str(metaObj.user_id))
        fileTable[fid]['cid'].append(cid)
        if cid not in pointerTable.keys():
            pointerTable[cid] = dict()
            pointerTable[cid]['reference'] = 0
            return True
        else:
            pointerTable[cid]['reference'] += 1
            return False

    def restore(self, metaObj):
        fileTable = self.fileMenu['filetable']
        fid = self.hash(metaObj.fileName + str(metaObj.user_id))
        if fid not in fileTable.keys():
            yield None, None
        else:
            for cid in fileTable[fid]['cid']:
                yield cid, fileTable[fid]['iv']

    def remove(self, metaObj):
        fileTable = self.fileMenu['filetable']
        pointerTable = self.fileMenu['pointertable']
        fid = self.hash(metaObj.fileName + str(metaObj.user_id))
        if fid not in fileTable.keys():
            return False
        else:
            candidate = []
            for cid in fileTable[fid]['cid']:
                logging.debug("Reference of cid {0}: {1}".format(cid, pointerTable[cid]['reference']))
                if pointerTable[cid]['reference'] < 1:
                    pointerTable.pop(cid, None)
                    candidate.append(cid)
                else:
                    pointerTable[cid]['reference'] -= 1
            logging.debug("Candidates: {0}".format(candidate))
            fileTable.pop(fid, None)
            return candidate


    def hash(self, data):
        hashObj = hashlib.sha256()
        if isinstance(data, bytes):
            hashObj.update(data)
        if isinstance(data, str):
            hashObj.update(data.encode('utf-8'))
        return hashObj.hexdigest()

    def save(self):
        with open(self.pickle, 'wb') as fout:
            pickle.dump(self.fileMenu, fout)

