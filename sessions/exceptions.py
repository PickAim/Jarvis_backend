import json

from starlette import status
from starlette.exceptions import HTTPException

JARVIS_EXCEPTION_KEY = 'jarvis_exception'
JARVIS_DESCRIPTION_KEY = 'description'


class JarvisExceptionsCode:
    # authorization exceptions
    INCORRECT_LOGIN_OR_PASSWORD = 1010

    # password correctness exceptions
    LESS_THAN_8 = 1020
    NOT_HAS_LOWER_LETTERS = 1030
    NOT_HAS_UPPER_LETTERS = 1040
    NOT_HAS_DIGIT = 1050
    NOT_HAS_SPECIAL_SIGNS = 1060
    HAS_WHITE_SPACES = 1070

    # registration exceptions
    REGISTER_EXISTING_LOGIN = 1080

    # token exceptions
    INCORRECT_TOKEN = 2010
    EXPIRED_TOKEN = 2020

    # accessible
    INCORRECT_GRANT_TYPE = 3010

    # incorrect requests
    INCORRECT_NICHE = 4010


class JarvisExceptions:
    @staticmethod
    def create_exception_with_code(exception_code: int, description: str = "") -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=json.dumps({
                JARVIS_EXCEPTION_KEY: exception_code,
                JARVIS_DESCRIPTION_KEY: 'Exception: ' + description
            })
        )

    INCORRECT_TOKEN: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_TOKEN, "Incorrect session token")

    EXPIRED_TOKEN: HTTPException = create_exception_with_code(JarvisExceptionsCode.EXPIRED_TOKEN, "Expired token")

    INCORRECT_LOGIN_OR_PASSWORD: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, "Incorrect login or password")

    EXISTING_LOGIN: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.REGISTER_EXISTING_LOGIN, "Existing login exception")

    INCORRECT_NICHE: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_NICHE, "Incorrect niche requested")
