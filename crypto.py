import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib


class Crypto:
    def __init__(self, fid, mode):
        if mode == 'client':
            self.__salt_iv = self._hash(fid).encode()
        if mode == 'ks':
            self.__salt_key = self._hash(fid).encode()

    def encode(self, chunk, key, iv):
        encryptor = Cipher(algorithms.AES(key),
                           modes.CFB(iv),
                           backend=default_backend()).encryptor()
        cipher = encryptor.update(chunk) + encryptor.finalize()
        return cipher

    def decode(self, cipher, key, iv):
        decryptor = Cipher(algorithms.AES(key),
                           modes.CFB(iv),
                           backend=default_backend()).decryptor()
        return decryptor.update(cipher) + decryptor.finalize()

    def _hash(self, data):
        hashObj = hashlib.sha256()
        if isinstance(data, bytes):
            hashObj.update(data)
        if isinstance(data, str):
            hashObj.update(data.encode('utf-8'))
        return hashObj.hexdigest()

    def gen_iv(self, data):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=16,
            salt=self.__salt_iv,
            iterations=100000,
            backend=default_backend()
        )
        if isinstance(data, str):
            iv = kdf.derive(data.encode())
        if isinstance(data, bytes):
            iv = kdf.derive(data)
        return iv

    def gen_key(self, chunk):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=16,
            salt=self.__salt_key,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(chunk)