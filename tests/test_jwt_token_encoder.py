import unittest
from datetime import datetime

import jwt

from Jarvis_backend.auth.tokens import PyJwtTokenEncoder


class JwtTokenEncoderTest(unittest.TestCase):
    def test_provide_token(self):
        key = 'secret'
        algorithm = 'HS256'
        data = {
            'id': 8,
            'date': int(datetime(year=2007, month=9, day=3).timestamp())
        }
        encoder = PyJwtTokenEncoder(key, algorithm)
        token = encoder.encode_token(data)
        decoded = jwt.decode(token, key=key, algorithms=[algorithm])
        for expected_pair, actual_pair in zip(data.items(), decoded.items(), strict=True):
            self.assertEqual(expected_pair, actual_pair)


if __name__ == '__main__':
    unittest.main()
