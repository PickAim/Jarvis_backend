from fastapi import APIRouter, Depends

from jarvis_backend.app.constants import UPDATE_TOKEN_USAGE_URL_PART
from jarvis_backend.app.tags import AUTH_TAG
from jarvis_backend.app.tokens.dependencies import update_token_correctness_post_depend, session_controller_depend
from jarvis_backend.app.tokens.util import save_and_return_session_tokens
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.support.request_api import RequestAPI


class TokenAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(tags=[AUTH_TAG])

    router = _router()
    router.prefix += UPDATE_TOKEN_USAGE_URL_PART

    @staticmethod
    @router.post('/update-all-tokens')
    def update_tokens(update_token: str = Depends(update_token_correctness_post_depend),
                      session_controller: JarvisSessionController = Depends(session_controller_depend)):
        new_access_token, new_update_token = session_controller.update_tokens(update_token)
        return save_and_return_session_tokens(new_access_token, new_update_token)
