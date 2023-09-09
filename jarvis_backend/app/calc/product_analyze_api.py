from datetime import datetime

from fastapi import Depends
from jorm.market.person import User, UserPrivilege

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import CalculationRequestAPI
from jarvis_backend.app.info_api import InfoAPI
from jarvis_backend.app.tokens.dependencies import session_controller_depend, access_token_correctness_post_depend
from jarvis_backend.sessions.dependencies import session_depend
from jarvis_backend.sessions.request_items import ProductDownturnResultModel, ProductTurnoverResultModel, \
    AllProductCalculateResultObject, ProductRequestModelWithMarketplaceId, \
    GetAllMarketplacesModel
from jarvis_backend.support.utils import extract_filtered_user_products_with_history


class ProductDownturnAPI(CalculationRequestAPI):
    PRODUCT_DOWNTURN_URL_PART = "/product-downturn"

    router = CalculationRequestAPI._router()
    router.prefix += PRODUCT_DOWNTURN_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate-all-in-marketplace/', response_model=ProductDownturnResultModel)
    def calculate_all_in_marketplace(request_data: ProductRequestModelWithMarketplaceId,
                                     access_token: str = Depends(access_token_correctness_post_depend),
                                     session=Depends(session_depend)) -> ProductDownturnResultModel:
        session_controller = session_controller_depend(session)
        user: User = ProductDownturnAPI.check_and_get_user(session_controller, access_token)
        filtered_user_products = extract_filtered_user_products_with_history(request_data, user.user_id,
                                                                             session_controller)
        return ProductDownturnResultModel.model_validate({"result_dict": {
            product_id: CalculationController.calc_downturn_days(filtered_user_products[product_id], datetime.utcnow())
            for product_id in filtered_user_products
        }})

    @staticmethod
    @router.post('/calculate/', response_model=dict[int, ProductDownturnResultModel])
    def calculate(access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)) \
            -> dict[int, ProductDownturnResultModel]:
        id_to_marketplace = InfoAPI.get_all_marketplaces(GetAllMarketplacesModel.model_validate({}), session=session)
        return {
            marketplace_id: ProductDownturnAPI.calculate_all_in_marketplace(
                ProductRequestModelWithMarketplaceId.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session=session
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
    @router.post('/calculate-all-in-marketplace/', response_model=ProductTurnoverResultModel)
    def calculate_all_in_marketplace(request_data: ProductRequestModelWithMarketplaceId,
                                     access_token: str = Depends(access_token_correctness_post_depend),
                                     session=Depends(session_depend)) -> ProductTurnoverResultModel:
        session_controller = session_controller_depend(session)
        user: User = ProductTurnoverAPI.check_and_get_user(session_controller, access_token)
        filtered_user_products = extract_filtered_user_products_with_history(request_data,
                                                                             user.user_id, session_controller)
        return ProductTurnoverResultModel.model_validate({"result_dict": {
            product_id: CalculationController.calc_turnover(filtered_user_products[product_id], datetime.utcnow())
            for product_id in filtered_user_products
        }})

    @staticmethod
    @router.post('/calculate/', response_model=dict[int, ProductTurnoverResultModel])
    def calculate(access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)) -> dict[int, ProductTurnoverResultModel]:
        id_to_marketplace = InfoAPI.get_all_marketplaces(GetAllMarketplacesModel.model_validate({}), session=session)
        return {
            marketplace_id: ProductTurnoverAPI.calculate_all_in_marketplace(
                ProductRequestModelWithMarketplaceId.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session=session
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
    def calculate_all_in_marketplace(request_data: ProductRequestModelWithMarketplaceId,
                                     access_token: str = Depends(access_token_correctness_post_depend),
                                     session=Depends(session_depend)) -> AllProductCalculateResultObject:
        session_controller = session_controller_depend(session)
        AllProductCalculateAPI.check_and_get_user(session_controller, access_token)
        result_dict = {
            'downturn': ProductDownturnAPI.calculate_all_in_marketplace(request_data, access_token, session=session),
            'turnover': ProductTurnoverAPI.calculate_all_in_marketplace(request_data, access_token, session=session)
        }
        return AllProductCalculateResultObject.model_validate(result_dict)

    @staticmethod
    @router.post('/calculate/', response_model=dict[int, AllProductCalculateResultObject])
    def calculate(access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)) -> dict[int, AllProductCalculateResultObject]:
        id_to_marketplace = InfoAPI.get_all_marketplaces(GetAllMarketplacesModel.model_validate({}), session=session)
        return {
            marketplace_id: AllProductCalculateAPI.calculate_all_in_marketplace(
                ProductRequestModelWithMarketplaceId.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session=session
            )
            for marketplace_id in id_to_marketplace
        }
