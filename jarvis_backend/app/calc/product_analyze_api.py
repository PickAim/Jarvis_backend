from datetime import datetime

from fastapi import Depends
from jorm.market.person import User, UserPrivilege

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import CalculationRequestAPI
from jarvis_backend.app.info_api import InfoAPI
from jarvis_backend.app.tokens.dependencies import session_controller_depend, access_token_correctness_post_depend
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.request_items import ProductDownturnResultObject, ProductTurnoverResultObject, \
    AllProductCalculateResultObject, ProductRequestObjectWithMarketplaceId, \
    GetAllMarketplacesObject
from jarvis_backend.support.utils import extract_filtered_user_products


class ProductDownturnAPI(CalculationRequestAPI):
    PRODUCT_DOWNTURN_URL_PART = "/product-downturn"

    router = CalculationRequestAPI._router()
    router.prefix += PRODUCT_DOWNTURN_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=ProductDownturnResultObject)
    def calculate_all_in_marketplace(request_data: ProductRequestObjectWithMarketplaceId,
                                     access_token: str = Depends(access_token_correctness_post_depend),
                                     session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = ProductDownturnAPI.check_and_get_user(session_controller, access_token)
        filtered_user_products = extract_filtered_user_products(request_data, user.user_id, session_controller)
        return ProductDownturnResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_downturn_days(filtered_user_products[product_id], datetime.utcnow())
            for product_id in filtered_user_products
        }})

    @staticmethod
    @router.post('/calculate/', response_model=dict[int, ProductDownturnResultObject])
    def calculate(access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        id_to_marketplace = InfoAPI.get_all_marketplaces(GetAllMarketplacesObject.model_validate({}),
                                                         session_controller)
        return {
            marketplace_id: ProductDownturnAPI.calculate_all_in_marketplace(
                ProductRequestObjectWithMarketplaceId.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session_controller=session_controller
            )
            for marketplace_id in id_to_marketplace
        }


class ProductTurnoverAPI(CalculationRequestAPI):
    PRODUCT_TURNOVER_URL_PART = "/product-turnover"

    router = CalculationRequestAPI._router()
    router.prefix += PRODUCT_TURNOVER_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate-all-in-marketplace/', response_model=ProductTurnoverResultObject)
    def calculate_all_in_marketplace(request_data: ProductRequestObjectWithMarketplaceId,
                                     access_token: str = Depends(access_token_correctness_post_depend),
                                     session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = ProductTurnoverAPI.check_and_get_user(session_controller, access_token)
        filtered_user_products = extract_filtered_user_products(request_data, user.user_id, session_controller)
        return ProductTurnoverResultObject.model_validate({"result_dict": {
            product_id: CalculationController.calc_turnover(filtered_user_products[product_id], datetime.utcnow())
            for product_id in filtered_user_products
        }})

    @staticmethod
    @router.post('/calculate/', response_model=dict[int, ProductTurnoverResultObject])
    def calculate(access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        id_to_marketplace = InfoAPI.get_all_marketplaces(GetAllMarketplacesObject.model_validate({}),
                                                         session_controller)
        return {
            marketplace_id: ProductTurnoverAPI.calculate_all_in_marketplace(
                ProductRequestObjectWithMarketplaceId.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session_controller=session_controller
            )
            for marketplace_id in id_to_marketplace
        }


class AllProductCalculateAPI(CalculationRequestAPI):
    ALL_PRODUCT_CALCULATE_URL_PART = "/all-product-calculation"

    router = CalculationRequestAPI._router()
    router.prefix += ALL_PRODUCT_CALCULATE_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate-all-in-marketplace/', response_model=AllProductCalculateResultObject)
    def calculate_all_in_marketplace(request_data: ProductRequestObjectWithMarketplaceId,
                                     access_token: str = Depends(access_token_correctness_post_depend),
                                     session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> AllProductCalculateResultObject:
        AllProductCalculateAPI.check_and_get_user(session_controller, access_token)
        result_dict = {
            'downturn': ProductDownturnAPI.calculate_all_in_marketplace(request_data, access_token, session_controller),
            'turnover': ProductTurnoverAPI.calculate_all_in_marketplace(request_data, access_token, session_controller)
        }
        return AllProductCalculateResultObject.model_validate(result_dict)

    @staticmethod
    @router.post('/calculate/', response_model=dict[int, AllProductCalculateResultObject])
    def calculate(access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> dict[int, AllProductCalculateResultObject]:
        id_to_marketplace = InfoAPI.get_all_marketplaces(GetAllMarketplacesObject.model_validate({}),
                                                         session_controller)
        return {
            marketplace_id: AllProductCalculateAPI.calculate_all_in_marketplace(
                ProductRequestObjectWithMarketplaceId.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session_controller=session_controller
            )
            for marketplace_id in id_to_marketplace
        }
