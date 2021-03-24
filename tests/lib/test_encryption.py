from unittest import TestCase
from lib import encryption


class EncryptionTestCase(TestCase):

    def test_pad_unpad(self) -> None:
        encdec = encryption.EncDec()
        string = 'Lorem ipsum'

        padded = encdec._padString(string)
        unpadded = encdec._unpadString(padded)

        self.assertEqual(bytes(string.encode('utf-8')), unpadded)

    def test_passwordToKey(self) -> None:
        encdec = encryption.EncDec()
        password = 'password'
        key = b"^\x88H\x98\xda(\x04qQ\xd0\xe5o\x8d\xc6)'s`=\rj\xab\xbd\xd6*\x11\xefr\x1d\x15B\xd8"
        result = encdec._passwordToKey(password)

        self.assertEqual(key, result)

    def test_makeInitialiationVector_len(self) -> None:
        encdec = encryption.EncDec()
        size = 16
        result = encdec._makeInitialiationVector(size)

        self.assertEqual(16, len(result))

    def test_encrypt_decrypt(self) -> None:
        encdec = encryption.EncDec()
        source = 'Lorem ipsum'
        password = 'password'

        encrypted = encdec.encrypt(source=source, password=password)
        decrypted = encdec.decrypt(source=encrypted, password=password)

        self.assertEqual(source, decrypted)

    def test_encrypt_decrypt_same_length_chunk_size_minus_1(self) -> None:
        # Edge case
        encdec = encryption.EncDec()
        source = '0123456789abcde'
        password = 'password'

        encrypted = encdec.encrypt(source=source, password=password)
        decrypted = encdec.decrypt(source=encrypted, password=password)

        self.assertEqual(source, decrypted)
