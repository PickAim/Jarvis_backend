from datetime import datetime

from fastapi import Depends, Body
from jorm.market.items import Product
from jorm.market.person import User, UserPrivilege
from jorm.support.utils import intersection

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import CalculationRequestAPI
from jarvis_backend.app.tokens.dependencies import session_controller_depend, access_token_correctness_post_depend
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.request_items import ProductDownturnResultObject, ProductTurnoverResultObject, \
    AllProductCalculateResultObject


def _extract_filtered_user_products(ids_to_filter: list[int],
                                    user_id: int, session_controller: JarvisSessionController) -> dict[int, Product]:
    user_products = session_controller.get_products_by_user(user_id)
    filtered_ids = intersection(user_products.keys(), ids_to_filter)
    return {
        product_id: user_products[product_id]
        for product_id in filtered_ids
    }


class ProductDownturnAPI(CalculationRequestAPI):
    PRODUCT_DOWNTURN_URL_PART = "/product-downturn"

    router = CalculationRequestAPI._router()
    router.prefix += PRODUCT_DOWNTURN_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=ProductDownturnResultObject)
    def calculate(product_ids: list[int] = Body([]),
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = ProductDownturnAPI.check_and_get_user(session_controller, access_token)
        filtered_user_products = _extract_filtered_user_products(product_ids, user.user_id, session_controller)
        return ProductDownturnResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_downturn_days(filtered_user_products[product_id], datetime.utcnow())
            for product_id in filtered_user_products
        }})


class ProductTurnoverAPI(CalculationRequestAPI):
    PRODUCT_TURNOVER_URL_PART = "/product-turnover"

    router = CalculationRequestAPI._router()
    router.prefix += PRODUCT_TURNOVER_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=ProductTurnoverResultObject)
    def calculate(product_ids: list[int] = Body([]),
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = ProductTurnoverAPI.check_and_get_user(session_controller, access_token)
        filtered_user_products = _extract_filtered_user_products(product_ids, user.user_id, session_controller)
        return ProductTurnoverResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_turnover(filtered_user_products[product_id], datetime.utcnow())
            for product_id in filtered_user_products
        }})


class AllProductCalculateAPI(CalculationRequestAPI):
    ALL_PRODUCT_CALCULATE_URL_PART = "/all-product-calculation"

    router = CalculationRequestAPI._router()
    router.prefix += ALL_PRODUCT_CALCULATE_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=AllProductCalculateResultObject)
    def calculate(product_ids: list[int] = Body([]),
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> AllProductCalculateResultObject:
        AllProductCalculateAPI.check_and_get_user(session_controller, access_token)
        result_dict = {
            'downturn': ProductDownturnAPI.calculate(product_ids, access_token, session_controller),
            'turnover': ProductTurnoverAPI.calculate(product_ids, access_token, session_controller)
        }
        return AllProductCalculateResultObject.model_validate(result_dict)
