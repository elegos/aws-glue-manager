import base64
from typing import Optional, Union
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
import os

import getpass


class CryptoException(Exception):
    pass


class EncDec:
    '''Encrption / Decryption class using AES CBC'''
    defaultPassword: str

    def __init__(self):
        rawDefaultPassword = getpass.getuser()
        if rawDefaultPassword == '':
            rawDefaultPassword = '7ba630f2-2dfa-4434-a550-93d3d4c6543b'

        defaultPasswordBytes = SHA256.new(data=bytes(
            rawDefaultPassword.encode('utf-8'))).digest()

        self.defaultPassword = base64.b64encode(
            defaultPasswordBytes).decode('utf-8')

    def encrypt(self, source: str, password: Optional[str] = None, encode: str = True) -> Union[bytes, str]:
        '''Encrypts the source with the given password
            source      str         the string to encrypt
            password    str, None   the password to encrypt the source with. If none, the default one will be used
            encode      bool, True  if True it will return a base64 string, otherwise the raw data
        '''
        if password is None:
            password = self.defaultPassword

        key = self._passwordToKey(password)
        IV = self._makeInitialiationVector()
        encryptor = AES.new(key=key, mode=AES.MODE_CBC, iv=IV)

        encrypted = IV + encryptor.encrypt(self._padString(source))

        return encrypted if not encode else base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, source: Union[str, bytes], password: Optional[str] = None, encode: bool = True) -> Union[bytes, str]:
        '''Decodes the source with the given password
            source      str|bytes   the string or bytes to decrypt. If string is passed, it will be base64-decoded
            password    str, None   the password to dencrypt the source with. If none, the default one will be used
            encode      bool, True  if True, the result will be encoded in a utf-8 string, otherwise the raw bytes will be returned
        '''
        if isinstance(source, str):
            source = base64.b64decode(source)

        if password is None:
            password = self.defaultPassword

        IV = source[:AES.block_size]
        encrypted = source[AES.block_size:]

        key = self._passwordToKey(password)
        decryptor = AES.new(key=key, mode=AES.MODE_CBC, iv=IV)

        decrypted = decryptor.decrypt(encrypted)
        unpadded = self._unpadString(decrypted)

        return unpadded if not encode else unpadded.decode('utf-8')

    def _padString(self, string: str, chunkSize: int = AES.block_size) -> bytes:
        '''Pads a string and prefix it with the padded amount
            string      str the string to pad
            chunkSize   int must be <= 256 (representable in 1 byte)
        '''
        if chunkSize > 256:
            raise CryptoException('Chunk size must be at most 256 (1 byte)')

        pad = (chunkSize - (len(string) + 1)) % chunkSize

        return bytes([pad]) + bytes(string.encode('utf-8')) + bytes([0] * pad)

    def _unpadString(self, source: bytes, chunkSize: int = AES.block_size) -> bytes:
        '''Unpads a bytes string removing the prefixed pad amount
            source      bytes   the bytes string to be unpadded, prefixed with 1 byte (see _padString)
            chunkSize   int     must be <= 256 (representable in 1 byte) and equal to the one used in _padString
        '''
        if chunkSize > 256:
            raise CryptoException('Chunk size is stored in 1 byte (<= 256)')

        pad = source[0]

        if pad == 0:
            return source[1:]

        return source[1:-pad]

    def _passwordToKey(self, password: str):
        return SHA256.new(data=bytes(password.encode('utf-8'))).digest()

    def _makeInitialiationVector(self, size=AES.block_size) -> bytes:
        return os.urandom(size)


# def encrypt(source: str, password: str = defaultPassword) -> bytes:
#     key = _password_to_key(password)
#     IV = make_initialization_vector()
#     encryptor = AES.new(key, AES.MODE_CBC, IV)

#     # store the IV at the beginning and encrypt
#     return IV + encryptor.encrypt(pad_string(string))


# def decrypt(string: str, password: str = defaultPassword) -> str:
#     key = _password_to_key(password)

#     # extract the IV from the beginning
#     IV = bytes(string[:AES.block_size].encode('latin-1'))
#     decryptor = AES.new(key, AES.MODE_CBC, IV)

#     string = decryptor.decrypt(
#         bytes(string[AES.block_size:].encode('latin-1')))
#     return unpad_string(string)

def pad_string(string: str, chunk_size: int = AES.block_size) -> bytes:
    """
    Pad string the peculirarity that uses the first byte
    is used to store how much padding is applied
    """
    assert chunk_size <= 256, 'We are using one byte to represent padding'
    to_pad = (chunk_size - (len(string) + 1)) % chunk_size

    return bytes([to_pad]) + bytes(string.encode('utf-8')) + bytes([0] * to_pad)


def unpad_string(string: str) -> str:
    to_pad = string[0]

    return string[1:-to_pad]


def encode(string: str) -> str:
    """
    Base64 encoding schemes are commonly used when there is a need to encode
    binary data that needs be stored and transferred over media that are
    designed to deal with textual data.
    This is to ensure that the data remains intact without
    modification during transport.
    """
    return base64.b64encode(string).decode("latin-1")


def decode(string: str):
    return base64.b64decode(string.encode("latin-1"))
