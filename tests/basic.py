import json
import unittest

from starlette.exceptions import HTTPException

from jarvis_backend.sessions.exceptions import JARVIS_EXCEPTION_KEY


class BasicServerTest(unittest.TestCase):
    def assertJarvisExceptionWithCode(self, expected_code: int, exception: HTTPException):
        self.assertEqual(500, exception.status_code,
                         msg=f'Expected JarvisException, but was [{type(exception)}]')
        self.assertTrue(JARVIS_EXCEPTION_KEY in exception.detail,
                        msg=f'Expected JarvisException, but was [{type(exception)}]')
        parsed_details = json.loads(exception.detail)
        actual_code = parsed_details[JARVIS_EXCEPTION_KEY]
        self.assertEqual(expected_code, actual_code,
                         msg=f'Expected code: [{expected_code}], but was [{actual_code}]')
