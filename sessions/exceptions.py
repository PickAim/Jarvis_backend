import json

from starlette import status
from starlette.exceptions import HTTPException


class JarvisExceptionsCode:
    # authorization exceptions
    INCORRECT_LOGIN_OR_PASSWORD = 1001

    # password correctness exceptions
    LESS_THAN_8 = 1002
    NOT_HAS_LOWER_LETTERS = 1003
    NOT_HAS_UPPER_LETTERS = 1004
    NOT_HAS_DIGIT = 1005
    NOT_HAS_SPECIAL_SIGNS = 1006
    HAS_WHITE_SPACES = 1007

    # registration exceptions
    REGISTER_EXISTING_LOGIN = 1008

    # token exceptions
    INCORRECT_TOKEN = 2001
    EXPIRED_TOKEN = 2002


class JarvisExceptions:
    @staticmethod
    def create_exception_with_code(exception_code: int, description: str = "") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=json.dumps({
                'jarvis_exception': exception_code,
                'description': 'Exception: ' + description
            })
        )

    INCORRECT_TOKEN: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_TOKEN, "Incorrect session token")

    EXPIRED_TOKEN: HTTPException = create_exception_with_code(JarvisExceptionsCode.EXPIRED_TOKEN, "Expired token")

    INCORRECT_LOGIN_OR_PASSWORD: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, "Incorrect login or password")

    EXISTING_LOGIN: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.REGISTER_EXISTING_LOGIN, "Existing login exception")
