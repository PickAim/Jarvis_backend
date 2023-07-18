import re

import phonenumbers
from phonenumbers import NumberParseException

from sessions.exceptions import JarvisExceptionsCode, JarvisExceptions


class InputPreparer:
    __SPACES_PATTERN = re.compile(' +')

    def prepare_search_string(self, string: str):
        string = string.strip()
        string = re.sub(self.__SPACES_PATTERN, ' ', string)
        return string.lower()

    def prepare_phone_number(self, phone_number: str) -> str:
        phone_number = phone_number.replace("-", "")
        phone_number = phone_number.replace(" ", "")
        return self.__convert_to_international_number_format(phone_number)

    @staticmethod
    def __convert_to_international_number_format(phone_number: str) -> str:
        if not phone_number.startswith("+") and not phone_number.startswith("+8") and not phone_number.startswith("8"):
            phone_number = f"+{phone_number}"
        if phone_number.startswith("8"):
            phone_number = f"+7{phone_number[1:]}"
        return phone_number


class InputValidator:
    __LOWER_CASE_PATTERN = re.compile(r"[a-zа-я]")
    __UPPER_CASE_PATTERN = re.compile(r"[A-ZА-Я]")
    __DIGIT_CONTAINING_PATTERN = re.compile(r"\d")
    __SPECIAL_SIGNS_PATTERN = re.compile(r"[!@#$%^&*()_+~]")
    __WHITE_SPACE_CONTAINING_PATTERN = re.compile(r"[ \t\n]")

    def check_password_correctness(self, password: str) -> int:
        if len(password) < 8:
            return JarvisExceptionsCode.LESS_THAN_8
        if not re.search(self.__LOWER_CASE_PATTERN, password):
            return JarvisExceptionsCode.NOT_HAS_LOWER_LETTERS
        if not re.search(self.__UPPER_CASE_PATTERN, password):
            return JarvisExceptionsCode.NOT_HAS_UPPER_LETTERS
        if not re.search(self.__DIGIT_CONTAINING_PATTERN, password):
            return JarvisExceptionsCode.NOT_HAS_DIGIT
        if not re.search(self.__SPECIAL_SIGNS_PATTERN, password):
            return JarvisExceptionsCode.NOT_HAS_SPECIAL_SIGNS
        if re.search(self.__WHITE_SPACE_CONTAINING_PATTERN, password):
            return JarvisExceptionsCode.HAS_WHITE_SPACES
        return 0

    def check_phone_number_correctness(self, phone_number: str) -> int:
        if re.search(self.__LOWER_CASE_PATTERN, phone_number) or re.search(self.__UPPER_CASE_PATTERN, phone_number):
            return JarvisExceptionsCode.INVALID_PHONE_NUMBER
        try:
            parsed_number = phonenumbers.parse(phone_number)
            if not phonenumbers.is_valid_number(parsed_number):
                return JarvisExceptionsCode.INVALID_PHONE_NUMBER
            return 0
        except NumberParseException as e:
            raise JarvisExceptions.create_exception_with_code(JarvisExceptionsCode.INVALID_PHONE_NUMBER, str(e))
