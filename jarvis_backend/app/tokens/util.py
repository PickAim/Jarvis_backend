from starlette.responses import JSONResponse

from jarvis_backend.app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from jarvis_backend.controllers.cookie import CookieHandler


def save_and_return_session_tokens(access_token: str, update_token: str):
    response: JSONResponse = JSONResponse(content={
        ACCESS_TOKEN_NAME: access_token,
        UPDATE_TOKEN_NAME: update_token,
    })
    CookieHandler.save_access_token(response, access_token)
    CookieHandler.save_update_token(response, update_token)
    return response


def save_and_return_all_tokens(access_token: str, update_token: str, imprint_token: str):
    response: JSONResponse = JSONResponse(content={
        ACCESS_TOKEN_NAME: access_token,
        UPDATE_TOKEN_NAME: update_token,
        IMPRINT_TOKEN_NAME: imprint_token
    })
    CookieHandler.save_access_token(response, access_token)
    CookieHandler.save_update_token(response, update_token)
    CookieHandler.save_imprint_token(response, imprint_token)
    return response
