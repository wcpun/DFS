import hashlib
import pickle
import os.path


class KeyMenu:
    def __init__(self):
        self.pickle = "key.pickle"
        self.keyMenu = dict()
        if not os.path.exists(self.pickle):
            self.keyMenu['fids'] = list()
            self.keyMenu['keys'] = dict()
        else:
            with open(self.pickle, 'rb') as fin:
                self.keyMenu = pickle.load(fin)

    def isExist(self, fid):
        fid = self.hash(fid)
        if fid not in self.keyMenu['fids']:
            self.keyMenu['fids'].append(fid)
            self.keyMenu['keys'][fid] = list()
            return False
        else:
            return True

    def push(self, fid, key):
        fid = self.hash(fid)
        try:
            self.keyMenu['keys'][fid].append(key)
            return True
        except KeyError:
            return False

    def pop(self, fid):
        fid = self.hash(fid)
        if fid not in self.keyMenu['fids']:
            yield None
        else:
            for key in self.keyMenu['keys'][fid]:
                yield key

    def remove(self, fid):
        fid = self.hash(fid)
        if fid not in self.keyMenu['fids']:
            return False
        else:
            self.keyMenu['fids'].remove(fid)
            self.keyMenu['keys'].pop(fid)
            return True

    def hash(self, data):
        hashObj = hashlib.sha256()
        if isinstance(data, bytes):
            hashObj.update(data)
        if isinstance(data, str):
            hashObj.update(data.encode('utf-8'))
        return hashObj.hexdigest()

    def save(self):
        with open(self.pickle, 'wb') as fout:
            pickle.dump(self.keyMenu, fout)
