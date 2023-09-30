from fastapi import APIRouter, Depends

from jarvis_backend.app.tags import INFO_TAG
from jarvis_backend.sessions.dependencies import session_controller_depend, session_depend
from jarvis_backend.sessions.request_items import (GetAllMarketplacesModel,
                                                   GetAllNichesModel,
                                                   GetAllCategoriesModel, BasicMarketplaceInfoModel)
from jarvis_backend.support.request_api import RequestAPI


class InfoAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(tags=[INFO_TAG])

    router = _router()

    @staticmethod
    @router.post('/get-all-marketplaces/', response_model=dict[int, str])
    def get_all_marketplaces(request_data: GetAllMarketplacesModel = None,
                             session=Depends(session_depend)) -> dict[int, str]:
        session_controller = session_controller_depend(session)
        is_allow_defaults = request_data.is_allow_defaults if request_data is not None else False
        return session_controller.get_all_marketplaces(is_allow_defaults)

    @staticmethod
    @router.post('/get-all-categories/', response_model=dict[int, str])
    def get_all_categories(request_data: GetAllCategoriesModel,
                           session=Depends(session_depend)) -> dict[int, str]:
        session_controller = session_controller_depend(session)
        return session_controller.get_all_categories(request_data.marketplace_id, request_data.is_allow_defaults)

    @staticmethod
    @router.post('/get-all-niches/', response_model=dict[int, str])
    def get_all_niches(request_data: GetAllNichesModel,
                       session=Depends(session_depend)) -> dict[int, str]:
        session_controller = session_controller_depend(session)
        return session_controller.get_all_niches(request_data.category_id, request_data.is_allow_defaults)

    @staticmethod
    @router.post('/get-all-warehouses/', response_model=dict[int, str])
    def get_all_warehouses(request_data: BasicMarketplaceInfoModel,
                           session=Depends(session_depend)) -> dict[int, str]:
        session_controller = session_controller_depend(session)
        return session_controller.get_all_warehouses(request_data.marketplace_id)
