import hashlib
from Crypto.Cipher import AES
from base64 import urlsafe_b64decode, urlsafe_b64encode

from django.conf import settings


class AESCryptor:
    """ AES 加密器 """

    def __init__(self):
        self.__encryptKey = settings.SECRET_KEY
        self.__key = hashlib.md5(self.__encryptKey.encode("utf8")).digest()

    @staticmethod
    def pad(text, block_size=32):
        pad = block_size - (len(text) % block_size)
        return (text + pad * chr(pad)).encode("utf8")

    @staticmethod
    def un_pad(text):
        index = text[-1]
        return text[:-index].decode("utf8")

    def encode(self, plaintext):
        """ AES 加密 """
        ciphertext = AES.new(
            self.__key, AES.MODE_ECB
        ).encrypt(self.pad(plaintext))
        return urlsafe_b64encode(ciphertext).decode("utf8").rstrip("=")

    def decode(self, ciphertext):
        """ AES 解密 """
        ciphertext = urlsafe_b64decode(
            ciphertext + "=" * (4 - len(ciphertext) % 4))
        cipher = AES.new(self.__key, AES.MODE_ECB)
        return self.un_pad(cipher.decrypt(ciphertext))
