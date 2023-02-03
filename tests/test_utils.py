import unittest

from utils.hashing import Hasher


class UtilsTest(unittest.TestCase):
    def test_hasher_verify(self):
        password: str = "password"
        hasher = Hasher()
        hashed = hasher.hash(password)
        print(hashed)
        self.assertTrue(hasher.verify(password, hashed))


if __name__ == '__main__':
    unittest.main()
