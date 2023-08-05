from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.support.input import InputValidator, InputPreparer


class InputController:
    @staticmethod
    def process_phone_number(phone_number: str) -> str:
        if phone_number is None or phone_number == '':
            return ''
        input_preparer = InputPreparer()
        input_validator = InputValidator()
        phone_number = input_preparer.prepare_phone_number(phone_number)
        phone_check_status = input_validator.check_phone_number_correctness(phone_number)
        if phone_check_status != 0:
            raise JarvisExceptions.create_exception_with_code(phone_check_status, "Phone number check failed")
        return phone_number

    @staticmethod
    def process_password(password: str) -> str:
        input_validator = InputValidator()
        password_check_status: int = input_validator.check_password_correctness(password)
        if password_check_status != 0:
            raise JarvisExceptions.create_exception_with_code(password_check_status, "Password check failed")
        return password

    @staticmethod
    def process_email(email: str) -> str:
        if email is None or email == '':
            return ''
        email = email.strip()
        input_validator = InputValidator()
        email_check_status = input_validator.check_email_correctness(email)
        if email_check_status != 0:
            raise JarvisExceptions.create_exception_with_code(email_check_status, "Email check failed")
        return email
