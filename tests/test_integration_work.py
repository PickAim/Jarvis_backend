import json
import unittest

from app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from app.session_requests import reg, auth, auth_by_token, log_out
from app.tokens.requests import update_tokens
from sessions.request_items import AuthenticationObject


class IntegrationTest(unittest.TestCase):
    def test_integration_work(self):
        object_params = {
            "email": "any@mail.com",
            "password": "MyPass1234!",
            "phone": "+78914561245"
        }
        auth_item = AuthenticationObject.parse_obj(object_params)

        # Registration
        response = reg(auth_item)
        self.assertIsNone(response)

        # Authorization
        response = auth(AuthenticationObject.parse_obj(auth_item), None)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)
        self.assertTrue(IMPRINT_TOKEN_NAME in response_dict)

        access_token = response_dict[ACCESS_TOKEN_NAME]
        update_token = response_dict[UPDATE_TOKEN_NAME]
        imprint_token = response_dict[IMPRINT_TOKEN_NAME]

        # Auth with token using
        response = auth_by_token(access_token, imprint_token)
        self.assertTrue(response)

        # Try to update tokens
        response = update_tokens(update_token)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)

        access_token = response_dict[ACCESS_TOKEN_NAME]
        update_token = response_dict[UPDATE_TOKEN_NAME]

        # Logout
        response = log_out(access_token, imprint_token)
        self.assertIsNotNone(response)


if __name__ == '__main__':
    unittest.main()
