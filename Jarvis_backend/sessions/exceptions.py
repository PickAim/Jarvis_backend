from enum import Enum

from fastapi import HTTPException
from starlette import status


class JarvisExceptionsCode(Enum):
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
    EXPIRED_TOKEN: int = 5002


class JarvisExceptions(Enum):
    INCORRECT_TOKEN = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=JarvisExceptionsCode.INCORRECT_TOKEN,
    )

    EXPIRED_TOKEN = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=JarvisExceptionsCode.EXPIRED_TOKEN
    )

    INCORRECT_LOGIN_OR_PASSWORD = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD,
    )

    EXISTING_LOGIN = HTTPException(
        status_code=status.HTTP_208_ALREADY_REPORTED,
        detail=JarvisExceptionsCode.REGISTER_EXISTING_LOGIN
    )
