import json
import unittest

from starlette.exceptions import HTTPException

from jarvis_backend.sessions.controllers import InputController
from jarvis_backend.sessions.exceptions import JARVIS_EXCEPTION_KEY, JarvisExceptionsCode


class ValidationTest(unittest.TestCase):
    def test_invalid_country_code_phone_number_validation(self):
        phone_number = "+89092865488"
        with self.assertRaises(HTTPException):
            InputController.process_phone_number(phone_number)

    def test_invalid_phone_number_validation(self):
        phone_number = "+a8909286d5488d"
        with self.assertRaises(HTTPException):
            InputController.process_phone_number(phone_number)

    def test_phone_number_validation(self):
        phone_number = "+79092865488"
        result_phone_number = InputController.process_phone_number(phone_number)
        self.assertEqual(phone_number, result_phone_number)

    def test_phone_number_recovery_on_validation(self):
        phone_number = "- 7909 286 548 8  "
        result_phone_number = InputController.process_phone_number(phone_number)
        self.assertEqual("+79092865488", result_phone_number)

    def assertJarvisExceptionWithCode(self, expected_code: int, exception: HTTPException):
        self.assertEqual(500, exception.status_code)
        self.assertTrue(JARVIS_EXCEPTION_KEY in exception.detail)
        parsed_details = json.loads(exception.detail)
        self.assertEqual(expected_code, parsed_details[JARVIS_EXCEPTION_KEY])

    def test_valid_password_validation(self):
        password = "Apassword123!"
        result_password = InputController.process_password(password)
        self.assertEqual(password, result_password)

    def test_password_without_uppercase_validation(self):
        password = "apassword123!"
        with self.assertRaises(HTTPException) as catcher:
            InputController.process_password(password)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.NOT_HAS_UPPER_LETTERS, catcher.exception)

    def test_password_without_lowercase_validation(self):
        password = "APASSWORD123!"
        with self.assertRaises(HTTPException) as catcher:
            InputController.process_password(password)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.NOT_HAS_LOWER_LETTERS, catcher.exception)

    def test_password_without_digit_validation(self):
        password = "Apassword!"
        with self.assertRaises(HTTPException) as catcher:
            InputController.process_password(password)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.NOT_HAS_DIGIT, catcher.exception)

    def test_password_without_special_signs_validation(self):
        password = "Apassword123"
        with self.assertRaises(HTTPException) as catcher:
            InputController.process_password(password)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.NOT_HAS_SPECIAL_SIGNS, catcher.exception)

    def test_password_with_spaces_signs_validation(self):
        password = "Apassword 123!"
        with self.assertRaises(HTTPException) as catcher:
            InputController.process_password(password)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.HAS_WHITE_SPACES, catcher.exception)

    def test_password_with_white_spaces_signs_validation(self):
        password = "Ap\nass\tword123!"
        with self.assertRaises(HTTPException) as catcher:
            InputController.process_password(password)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.HAS_WHITE_SPACES, catcher.exception)

    def test_email_validation(self):
        email = "myEmail@mail.ngs.com"
        result_email = InputController.process_email(email)
        self.assertEqual(email, result_email)

    def test_invalid_email_validation(self):
        email = "myEmail.ngs.com"
        with self.assertRaises(HTTPException) as catcher:
            InputController.process_email(email)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INVALID_EMAIL, catcher.exception)


if __name__ == '__main__':
    unittest.main()
