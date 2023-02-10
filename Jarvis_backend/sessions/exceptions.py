import json

from starlette import status
from starlette.exceptions import HTTPException


class JarvisExceptionsCode:
    # authorization exceptions
    INCORRECT_LOGIN_OR_PASSWORD = 4012

    # password correctness exceptions
    LESS_THAN_8 = 4013
    NOT_HAS_LOWER_LETTERS = 4014
    NOT_HAS_UPPER_LETTERS = 4015
    NOT_HAS_DIGIT = 4016
    NOT_HAS_SPECIAL_SIGNS = 4017
    HAS_WHITE_SPACES = 4018

    # registration exceptions
    REGISTER_EXISTING_LOGIN = 4019

    # token exceptions
    INCORRECT_TOKEN = 5001
    EXPIRED_TOKEN = 5002


class JarvisExceptions:
    @staticmethod
    def create_exception_with_code(exception_code: int) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=json.dumps({
                'jarvis_exception': exception_code
            })
        )

    INCORRECT_TOKEN: HTTPException = create_exception_with_code(JarvisExceptionsCode.INCORRECT_TOKEN)

    EXPIRED_TOKEN: HTTPException = create_exception_with_code(JarvisExceptionsCode.EXPIRED_TOKEN)

    INCORRECT_LOGIN_OR_PASSWORD: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD)

    EXISTING_LOGIN: HTTPException = create_exception_with_code(JarvisExceptionsCode.REGISTER_EXISTING_LOGIN)
