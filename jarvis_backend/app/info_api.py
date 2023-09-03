from fastapi import APIRouter, Depends

from jarvis_backend.app.tags import INFO_TAG
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend
from jarvis_backend.sessions.request_items import (GetAllMarketplacesModel,
                                                   GetAllNichesModel,
                                                   GetAllCategoriesModel)
from jarvis_backend.support.request_api import RequestAPI


class InfoAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(tags=[INFO_TAG])

    router = _router()

    @staticmethod
    @router.post('/get-all-marketplaces/', response_model=dict[int, str])
    def get_all_marketplaces(request_data: GetAllMarketplacesModel = None,
                             session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        is_allow_defaults = request_data.is_allow_defaults if request_data is not None else False
        return session_controller.get_all_marketplaces(is_allow_defaults)

    @staticmethod
    @router.post('/get-all-categories/', response_model=dict[int, str])
    def get_all_categories(request_data: GetAllCategoriesModel,
                           session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_categories(request_data.marketplace_id, request_data.is_allow_defaults)

    @staticmethod
    @router.post('/get-all-niches/', response_model=dict[int, str])
    def get_all_niches(request_data: GetAllNichesModel,
                       session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_niches(request_data.category_id, request_data.is_allow_defaults)
