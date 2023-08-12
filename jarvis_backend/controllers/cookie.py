from fastapi import Cookie
from starlette.responses import JSONResponse, Response

from jarvis_backend.app.constants import ACCESS_TOKEN_USAGE_URL_PART, UPDATE_TOKEN_USAGE_URL_PART

COOKIE_ACCESS_NAME = "cookie_access_token"
COOKIE_UPDATE_NAME = "cookie_update_token"
COOKIE_IMPRINT_NAME = "cookie_imprint_token"


class CookieHandler:
    @staticmethod
    def save_access_token(response: Response, access_token: str) -> Response:
        response.set_cookie(key=COOKIE_ACCESS_NAME, path=ACCESS_TOKEN_USAGE_URL_PART,
                            value=access_token, httponly=True, secure=True)
        return response

    @staticmethod
    def save_update_token(response: Response, update_token: str) -> Response:
        response.set_cookie(key=COOKIE_UPDATE_NAME, value=update_token, httponly=True,
                            secure=True)
        return response

    @staticmethod
    def save_imprint_token(response: Response, imprint_token: str) -> Response:
        response.set_cookie(key=COOKIE_IMPRINT_NAME, value=imprint_token, httponly=True, secure=True)
        return response

    @staticmethod
    def load_access_token(cookie_access_token: str = Cookie(default=None)) -> str | None:
        return cookie_access_token

    @staticmethod
    def load_update_token(cookie_update_token: str = Cookie(default=None)) -> str | None:
        return cookie_update_token

    @staticmethod
    def load_imprint_token(cookie_imprint_token: str = Cookie(default=None)) -> str | None:
        return cookie_imprint_token

    @staticmethod
    def delete_all_cookie(response: JSONResponse) -> JSONResponse:
        response.delete_cookie(COOKIE_ACCESS_NAME, path=ACCESS_TOKEN_USAGE_URL_PART, httponly=True, secure=True)
        response.delete_cookie(COOKIE_UPDATE_NAME, path=UPDATE_TOKEN_USAGE_URL_PART, httponly=True, secure=True)
        return response
