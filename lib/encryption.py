import base64
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

import getpass

defaultKey = getpass.getuser()
if defaultKey == '':
    defaultKey = '7ba630f2-2dfa-4434-a550-93d3d4c6543b'


def encrypt(source: str, key: str = defaultKey, encode: bool = True) -> str:
    # use SHA-256 over our key to get a proper-sized AES key
    key = SHA256.new(bytes(key, encoding='utf-8')).digest()
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    # calculate needed padding
    padding = AES.block_size - len(source) % AES.block_size
    source = bytes(source, encoding='utf-8') + bytes([padding]) * padding
    # store the IV at the beginning and encrypt
    data = IV + encryptor.encrypt(source)

    return base64.b64encode(data).decode("latin-1") if encode else data


def decrypt(source, key: str = defaultKey, decode=True) -> str:
    if decode:
        source = base64.b64decode(source.encode("latin-1"))
    # use SHA-256 over our key to get a proper-sized AES key
    key = SHA256.new(bytes(key, encoding='utf-8')).digest()
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    # pick the padding value from the end; Python 2.x: ord(data[-1])
    padding = data[-1]
    # Python 2.x: chr(padding) * padding
    if data[-padding:] != bytes([padding]) * padding:
        raise ValueError("Invalid padding...")
    return str(data[:-padding], encoding='utf-8')  # remove the padding
