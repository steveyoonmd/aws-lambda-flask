import secrets
from base64 import b64encode, b64decode

from libs.utils import md5hex

crypto_imported = True
try:
    from Crypto.Cipher import AES
    # from Crypto import Random
except ImportError as ex:
    print(ex)
    crypto_imported = False


class AESCrypto:
    def __init__(self, key):
        self.key = md5hex(key)

    @classmethod
    def pad(cls, s):
        padding = AES.block_size - (len(s.encode('utf-8')) % AES.block_size)
        return s + (padding * chr(padding))

    @classmethod
    def unpad(cls, s):
        return s[:-ord(s[len(s) - 1:])]

    def encrypt(self, plain_text):
        if not crypto_imported:
            return plain_text

        padded = self.pad(plain_text)

        # iv = Random.new().read(AES.block_size)
        iv = secrets.token_bytes(AES.block_size)
        aes_new = AES.new(self.key, AES.MODE_CBC, iv)

        encoded = b64encode(iv + aes_new.encrypt(padded)).decode('utf-8')

        # url safe base64
        return encoded.replace('+', '_')

    def decrypt(self, b64encoded):
        if not crypto_imported:
            return b64encoded

        # url safe base64
        replaced = b64encoded.replace('_', '+')
        decoded = b64decode(replaced)

        iv = decoded[:AES.block_size]
        aes_new = AES.new(self.key, AES.MODE_CBC, iv)

        return self.unpad(aes_new.decrypt(decoded[AES.block_size:])).decode('utf-8')
