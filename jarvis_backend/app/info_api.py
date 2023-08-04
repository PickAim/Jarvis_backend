from fastapi import APIRouter, Depends
from jorm.market.person import User

from jarvis_backend.app.tags import INFO_TAG
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend
from jarvis_backend.sessions.request_items import (GetAllMarketplacesObject,
                                                   GetAllNichesObject,
                                                   GetAllProductsObject, GetAllCategoriesObject)
from jarvis_backend.support.request_api import RequestAPI


class InfoAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(tags=[INFO_TAG])

    router = _router()

    @staticmethod
    @router.post('/get-all-marketplaces/', response_model=dict[int, str])
    def get_all_marketplaces(request_data: GetAllMarketplacesObject = None,
                             session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        is_allow_defaults = request_data.is_allow_defaults if request_data is not None else False
        return session_controller.get_all_marketplaces(is_allow_defaults)

    @staticmethod
    @router.post('/get-all-categories/', response_model=dict[int, str])
    def get_all_categories(request_data: GetAllCategoriesObject,
                           session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_categories(request_data.marketplace_id, request_data.is_allow_defaults)

    @staticmethod
    @router.post('/get-all-niches/', response_model=dict[int, str])
    def get_all_niches(request_data: GetAllNichesObject,
                       session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_niches(request_data.category_id, request_data.is_allow_defaults)

    @staticmethod
    @router.post('/get-all-in-marketplace-user-products/', response_model=dict[int, dict])
    def get_all_in_marketplace_user_products(request_data: GetAllProductsObject,
                                             access_token: str = Depends(access_token_correctness_post_depend),
                                             session_controller: JarvisSessionController = Depends(
                                                 session_controller_depend)
                                             ) -> dict[int, dict]:
        user: User = session_controller.get_user(access_token)
        user_products = session_controller.get_products_by_user(user.user_id, request_data.marketplace_id)
        return {
            product_id: {
                "global_id": user_products[product_id].global_id,
                "name": user_products[product_id].name,
                "category": user_products[product_id].category_name,
                "niche": user_products[product_id].niche_name,
                "cost": user_products[product_id].cost,
                "rating": user_products[product_id].rating,
                "seller": user_products[product_id].seller,
                "brand": user_products[product_id].brand,
                "history": {
                    history_unit.unit_date.timestamp(): history_unit.cost
                    for history_unit in user_products[product_id].history.get_history()
                }
            }
            for product_id in user_products
        }

    @staticmethod
    @router.post('/get-all-user-products/', response_model=dict[int, dict[int, dict]])
    def get_all_user_products(access_token: str = Depends(access_token_correctness_post_depend),
                              session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, dict]:
        id_to_marketplace = InfoAPI.get_all_marketplaces(GetAllMarketplacesObject.model_validate({}),
                                                         session_controller)
        return {
            marketplace_id: InfoAPI.get_all_in_marketplace_user_products(
                GetAllProductsObject.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session_controller=session_controller
            )
            for marketplace_id in id_to_marketplace
        }
