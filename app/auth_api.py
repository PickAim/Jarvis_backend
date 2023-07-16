from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.tags import AUTH_TAG
from app.tokens.dependencies import (
    imprint_token_correctness_depend,
    access_token_correctness_depend,
    session_controller_depend
)
from app.tokens.util import save_and_return_all_tokens
from sessions.controllers import CookieHandler, JarvisSessionController
from sessions.request_items import AuthenticationObject, RegistrationObject
from support.request_api import RequestAPI


class SessionAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter()

    router = _router()
    router.tags = [AUTH_TAG]

    @staticmethod
    @router.post('/reg/')
    def registrate_user(auth_item: RegistrationObject,
                        session_controller: JarvisSessionController = Depends(session_controller_depend)):
        session_controller.register_user(auth_item.email, auth_item.password, auth_item.phone)

    @staticmethod
    @router.post('/auth/', tags=[AUTH_TAG])
    def authenticate_user(auth_item: AuthenticationObject,
                          imprint_token: str | None = Depends(imprint_token_correctness_depend),
                          session_controller: JarvisSessionController = Depends(session_controller_depend)):
        new_access_token, new_update_token, new_imprint_token = \
            session_controller.authenticate_user(auth_item.login, auth_item.password, imprint_token)
        return save_and_return_all_tokens(new_access_token, new_update_token, new_imprint_token)

    @staticmethod
    @router.get(ACCESS_TOKEN_USAGE_URL_PART + '/auth/')
    def auth_by_token(_: str = Depends(access_token_correctness_depend),
                      __: str = Depends(imprint_token_correctness_depend)):
        return True

    @staticmethod
    @router.get(ACCESS_TOKEN_USAGE_URL_PART + '/logout/')
    def log_out(access_token: str = Depends(access_token_correctness_depend),
                imprint_token: str = Depends(imprint_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend)):
        session_controller.logout(access_token, imprint_token)
        response = JSONResponse(content="deleted")
        CookieHandler.delete_all_cookie(response)
        return response
