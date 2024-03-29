import json

from starlette import status
from starlette.exceptions import HTTPException

JARVIS_EXCEPTION_KEY = 'jarvis_exception'
JARVIS_DESCRIPTION_KEY = 'description'


class JarvisExceptionsCode:
    # registration exceptions
    REGISTER_EXISTING_LOGIN = 1000

    # authorization exceptions
    INCORRECT_LOGIN_OR_PASSWORD = 1010

    # password correctness exceptions
    LESS_THAN_8 = 1020
    NOT_HAS_LOWER_LETTERS = 1030
    NOT_HAS_UPPER_LETTERS = 1040
    NOT_HAS_DIGIT = 1050
    NOT_HAS_SPECIAL_SIGNS = 1060
    HAS_WHITE_SPACES = 1070

    # phone number correctness exceptions
    INVALID_PHONE_NUMBER = 1080

    # email correctness exceptions
    INVALID_EMAIL = 1090

    # token exceptions
    INCORRECT_TOKEN = 2010
    EXPIRED_TOKEN = 2020

    # accessibility
    INCORRECT_GRANT_TYPE = 3010

    # incorrect requests
    INCORRECT_NICHE = 4010
    INCORRECT_CATEGORY = 4020
    INCORRECT_MARKETPLACE = 4030
    INCORRECT_WAREHOUSE = 4040

    # session exceptions

    TIMEOUT = 5040

    INCORRECT_MARKETPLACE_API_KEY = 6010

    USER_FUCKS = 9090  # TODO think about naming


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

    REGISTER_WITHOUT_LOGIN: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD,
                                   "You not specify any login information")

    INCORRECT_TOKEN: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_TOKEN, "Incorrect session token")

    EXPIRED_TOKEN: HTTPException = create_exception_with_code(JarvisExceptionsCode.EXPIRED_TOKEN, "Expired token")

    INCORRECT_LOGIN_OR_PASSWORD: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, "Incorrect login or password")

    EXISTING_LOGIN: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.REGISTER_EXISTING_LOGIN, "Existing login exception")

    INCORRECT_NICHE: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_NICHE, "Incorrect niche requested")

    INCORRECT_CATEGORY: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_CATEGORY, "Incorrect category requested")

    INCORRECT_MARKETPLACE: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_MARKETPLACE, "Incorrect marketplace requested")

    INCORRECT_WAREHOUSE: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_WAREHOUSE, "Incorrect warehouse requested")

    INCORRECT_MARKETPLACE_API_KEY: HTTPException = \
        create_exception_with_code(JarvisExceptionsCode.INCORRECT_MARKETPLACE_API_KEY, "Incorrect marketplace API key")
