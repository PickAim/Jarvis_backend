from fastapi import APIRouter, Depends

from app.constants import UPDATE_TOKEN_USAGE_URL_PART
from app.tokens.dependencies import update_token_correctness_depend, session_controller_depend
from app.tokens.util import save_and_return_session_tokens
from sessions.controllers import JarvisSessionController
from support.request_api import RequestAPI, get


class TokenAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter()

    router = _router()

    @staticmethod
    @get(router, UPDATE_TOKEN_USAGE_URL_PART + '/update-all-tokens')
    def update_tokens(update_token: str = Depends(update_token_correctness_depend),
                      session_controller: JarvisSessionController = Depends(session_controller_depend)):
        new_access_token, new_update_token = session_controller.update_tokens(update_token)
        return save_and_return_session_tokens(new_access_token, new_update_token)
