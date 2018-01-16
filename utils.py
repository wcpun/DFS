class Meta:
    def __init__(self, user_id, fileName, fileSize=None, iv=None):
        self.user_id = user_id
        self.fileName = fileName
        self.fileSize = fileSize
        self.iv = iv

    def __str__(self):
        return "User ID: {0}\n".format(self.user_id) + \
               "File Name: {0}\n".format(self.fileName) + \
               "File Size: {0}\n".format(self.fileSize) + \
               "IV: {0}".format(self.iv)


class Code:
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return "Key: {0}".format(self.key)


class Cipher:
    def __init__(self, cipher):
        self.cipher = cipher

    def __str__(self):
        return "Cipher: {0}".format(self.cipher)


