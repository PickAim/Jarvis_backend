from fastapi import APIRouter, Depends

from app.tags import INFO_TAG
from sessions.controllers import JarvisSessionController
from sessions.dependencies import session_controller_depend
from support.request_api import RequestAPI


class InfoAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(tags=[INFO_TAG])

    router = _router()

    @staticmethod
    @router.get('/get-all-marketplaces/', response_model=dict[int, str])
    def get_all_marketplaces(session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_marketplaces()

    @staticmethod
    @router.get('/get-all-categories/', response_model=dict[int, str])
    def get_all_marketplaces(marketplace_id: int,
                             session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_categories(marketplace_id)

    @staticmethod
    @router.get('/get-all-niches/', response_model=dict[int, str])
    def get_all_niches(category_id: int, marketplace_id: int,
                       session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_niches(category_id, marketplace_id)
