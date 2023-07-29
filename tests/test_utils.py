import time
import unittest

from passlib.context import CryptContext
from starlette.exceptions import HTTPException

from jarvis_backend.auth.hashing.hasher import PasswordHasher
from jarvis_backend.auth.hashing.passlib_encoder import PasslibEncoder
from jarvis_backend.support.decorators import timeout


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

    def test_timeout_correctness(self):
        @timeout(0.15)
        def timeout_func(a, b):
            time.sleep(0.2)
            return a + b

        with self.assertRaises(HTTPException):
            timeout_func(1, 2)

    def test_not_timeout_correctness(self):
        @timeout()
        def timeout_func(a, b):
            time.sleep(0.2)
            return a + b

        result = timeout_func(1, 2)
        self.assertEqual(3, result)


if __name__ == '__main__':
    unittest.main()
