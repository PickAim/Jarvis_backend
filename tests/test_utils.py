import unittest

from auth.hashing import PasswordHasher


class UtilsTest(unittest.TestCase):
    def test_hasher_verify(self):
        password: str = "password"
        hasher: PasswordHasher = PasswordHasher()
        hashed: str = hasher.hash(password)
        print(hashed)
        self.assertTrue(hasher.verify(password, hashed))


if __name__ == '__main__':
    unittest.main()
