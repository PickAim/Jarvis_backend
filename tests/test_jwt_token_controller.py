import datetime
import unittest

from auth.tokens.token_control import TokenController


class TokenControllerTest(unittest.TestCase):
    TEST_SECRET_KEY = "abcdefghijklmnopqrstuvwxyz"

    def test_tokens_lifetime(self):
        tokenizer = TokenController(self.TEST_SECRET_KEY)
        access_token = tokenizer.create_access_token(123, datetime.timedelta(microseconds=1))
        update_token = tokenizer.create_update_token(123)
        imprint_token = tokenizer.create_imprint_token(123)

        self.assertTrue(tokenizer.is_token_expired(access_token))
        self.assertFalse(tokenizer.is_token_expired(update_token))
        self.assertFalse(tokenizer.is_token_expired(imprint_token))


if __name__ == '__main__':
    unittest.main()
