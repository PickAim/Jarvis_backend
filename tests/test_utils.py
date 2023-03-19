import unittest

from passlib.context import CryptContext

from auth.hashing.hasher import PasswordHasher
from auth.hashing.passlib_encoder import PasslibEncoder


class UtilsTest(unittest.TestCase):
    def test_hasher_verify(self):
        password: str = "password"
        context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        hasher: PasswordHasher = PasswordHasher(context)
        hashed: str = hasher.hash(password)
        print(hashed)
        self.assertTrue(hasher.verify(password, hashed))

    def test_passlib_encoder(self):
        context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        encoder = PasslibEncoder(context)
        password = "mypAss"
        hash_code = encoder.encode(password)
        print(hash_code)
        self.assertTrue(encoder.verify(password, hash_code))


if __name__ == '__main__':
    unittest.main()
