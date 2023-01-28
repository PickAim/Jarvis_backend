from enum import Enum


class JarvisException(Enum):
    # authorization exceptions
    INCORRECT_LOGIN_OR_PASSWORD: int = 4012

    # password correctness exceptions
    LESS_THAN_8: int = 4013
    NOT_HAS_LOWER_LETTERS: int = 4014
    NOT_HAS_UPPER_LETTERS: int = 4015
    NOT_HAS_DIGIT: int = 4016
    NOT_HAS_SPECIAL_SIGNS: int = 4017
    HAS_WHITE_SPACES: int = 4018

    # registration exceptions
    REGISTER_EXISTING_LOGIN: int = 4019

    INCORRECT_TOKEN: int = 5001
