from fastapi import APIRouter, Depends
from jarvis_factory.factories.jorm import JORMClassesFactory

from jarvis_backend.app.tags import INFO_TAG
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
    def get_all_user_products():  # TODO add access token and session controller parameter
        default_niche = JORMClassesFactory.create_default_niche()
        products = default_niche.products[:10]
        return {
            i: {
                "global_id": products[i].global_id,
                "name": products[i].name,
                "category": products[i].category_name,
                "niche": products[i].niche_name,
                "cost": products[i].cost,
                "rating": products[i].rating,
                "seller": products[i].seller,
                "brand": products[i].brand,
                "history": {
                    history_unit.unit_date.timestamp(): history_unit.cost
                    for history_unit in products[i].history.get_history()
                }
            }
            for i in range(len(products))
        }
