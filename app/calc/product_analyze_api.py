from datetime import datetime

from fastapi import Depends
from jorm.market.person import User, UserPrivilege

from app.calc.calculation import CalculationController
from app.calc.calculation_request_api import CalculationRequestAPI
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend
from sessions.controllers import JarvisSessionController
from sessions.request_items import ProductDownturnResultObject, ProductTurnoverResultObject


class ProductDownturnAPI(CalculationRequestAPI):
    PRODUCT_DOWNTURN_URL_PART = "/product-downturn"

    router = CalculationRequestAPI._router()
    router.prefix += PRODUCT_DOWNTURN_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=ProductDownturnResultObject)
    def calculate(access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = ProductDownturnAPI.check_and_get_user(session_controller, access_token)
        user_products = session_controller.get_products_by_user(user.user_id)
        if user_products is None:
            return ProductDownturnResultObject.model_validate({"result_dict": {}})
        return ProductDownturnResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_downturn_days(user_products[product_id], datetime.utcnow())
            for product_id in user_products
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
    def calculate(access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = session_controller.get_user(access_token)
        user_products = session_controller.get_products_by_user(user.user_id)
        if user_products is None:
            return ProductTurnoverResultObject.model_validate({"result_dict": {}})
        return ProductTurnoverResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_turnover(user_products[product_id], datetime.utcnow())
            for product_id in user_products
        }})
