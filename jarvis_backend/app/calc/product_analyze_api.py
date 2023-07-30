from datetime import datetime

from fastapi import Depends, Body
from jorm.market.person import User, UserPrivilege
from jorm.support.utils import intersection

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import CalculationRequestAPI
from jarvis_backend.app.tokens.dependencies import session_controller_depend, access_token_correctness_post_depend
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.request_items import ProductDownturnResultObject, ProductTurnoverResultObject


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
        user_products = session_controller.get_products_by_user(user.user_id)
        if user_products is None:
            return ProductDownturnResultObject.model_validate({"result_dict": {}})
        filtered_ids = intersection(user_products.keys(), product_ids)
        return ProductDownturnResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_downturn_days(user_products[product_id], datetime.utcnow())
            for product_id in filtered_ids
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
        user: User = session_controller.get_user(access_token)
        user_products = session_controller.get_products_by_user(user.user_id)
        if user_products is None:
            return ProductTurnoverResultObject.model_validate({"result_dict": {}})
        filtered_ids = intersection(user_products.keys(), product_ids)
        return ProductTurnoverResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_turnover(user_products[product_id], datetime.utcnow())
            for product_id in filtered_ids
        }})
