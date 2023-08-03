from fastapi import APIRouter, Depends
from jorm.market.person import User

from jarvis_backend.app.constants import ACCESS_TOKEN_USAGE_URL_PART
from jarvis_backend.app.tags import USER_TAG
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend
from jarvis_backend.sessions.request_items import AddApiKeyObject, BaseApiKeyObject
from jarvis_backend.support.request_api import RequestAPI


class UserAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART, tags=[USER_TAG])

    router = _router()

    @staticmethod
    @router.post('/add-marketplace-api-key/')
    def add_marketplace_api_key(request_data: AddApiKeyObject,
                                access_token: str = Depends(access_token_correctness_post_depend),
                                session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = session_controller.get_user(access_token)
        session_controller.add_marketplace_api_key(request_data, user.user_id)

    @staticmethod
    @router.post('/get-all-marketplace-api-keys/', response_model=dict[int, str])
    def get_all_marketplace_api_keys(access_token: str = Depends(access_token_correctness_post_depend),
                                     session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = session_controller.get_user(access_token)
        return user.marketplace_keys

    @staticmethod
    @router.post('/delete-marketplace-api-key/')
    def delete_marketplace_api_key(request_data: BaseApiKeyObject,
                                   access_token: str = Depends(access_token_correctness_post_depend),
                                   session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = session_controller.get_user(access_token)
        session_controller.delete_marketplace_api_key(request_data, user.user_id)
