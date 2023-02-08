import unittest
from datetime import datetime

import jwt

from Jarvis_backend.auth import PyJwtTokenDecoder


class JwtTokenDecoderTest(unittest.TestCase):
    def test_extract_payload(self):
        data = {
            'id': 8,
            'date': int(datetime(year=2007, month=9, day=3).timestamp())
        }
        key = 'secret'
        algorithm = 'HS256'
        token = jwt.encode(data, key, algorithm)
        decoder = PyJwtTokenDecoder(key, [algorithm])
        payload = decoder.decode_payload(token)
        for expected_pair, actual_pair in zip(data.items(), payload.items(), strict=True):
            self.assertEqual(expected_pair, actual_pair)


if __name__ == '__main__':
    unittest.main()
