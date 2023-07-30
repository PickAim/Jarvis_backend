from fastapi import APIRouter, Depends
from jorm.market.person import User

from jarvis_backend.app.tags import INFO_TAG
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend
from jarvis_backend.support.request_api import RequestAPI


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
    def get_all_categories(marketplace_id: int,
                           session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_categories(marketplace_id)

    @staticmethod
    @router.get('/get-all-niches/', response_model=dict[int, str])
    def get_all_niches(category_id: int,
                       session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, str]:
        return session_controller.get_all_niches(category_id)

    @staticmethod
    @router.get('/get-all-user-products/')
    def get_all_user_products(access_token: str = Depends(access_token_correctness_post_depend),
                              session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = session_controller.get_user(access_token)
        user_products = session_controller.get_products_by_user(user.user_id)
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
