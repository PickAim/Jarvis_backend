from datetime import datetime

from fastapi import Depends
from jarvis_factory.factories.jdu import JDUClassesFactory
from jorm.market.items import Product
from jorm.market.person import User, UserPrivilege
from jorm.server.providers.providers import UserMarketDataProvider

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import CalculationRequestAPI
from jarvis_backend.app.info_api import InfoAPI
from jarvis_backend.app.tokens.dependencies import session_controller_depend, access_token_correctness_post_depend
from jarvis_backend.sessions.dependencies import session_depend
from jarvis_backend.sessions.request_items import ProductDownturnResultModel, ProductTurnoverResultModel, \
    AllProductCalculateResultObject, ProductRequestModelWithMarketplaceId, \
    GetAllMarketplacesModel, ProductKeywordsRequestModel, KeywordsRequestModel
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
        marketplace_id = request_data.marketplace_id
        product_ids = request_data.product_ids
        filtered_user_products = extract_filtered_user_products_with_history(marketplace_id, user.user_id,
                                                                             session_controller, product_ids)
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
        marketplace_id = request_data.marketplace_id
        product_ids = request_data.product_ids
        filtered_user_products = extract_filtered_user_products_with_history(marketplace_id, user.user_id,
                                                                             session_controller, product_ids)
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


class KeywordsAPI:
    @staticmethod
    def get_nearest_keywords(words: list[str],
                             user_market_data_provider: UserMarketDataProvider) -> dict[str, set[str]]:
        result: dict[str, set[str]] = {}
        check_set = set()
        for word in words:
            result[word] = set()
            try:
                nearest_words = user_market_data_provider.get_nearest_keywords(word)
            except Exception:
                continue
            for nearest_word in nearest_words:
                if nearest_word not in check_set:
                    result[word].add(nearest_word)
                    check_set.add(nearest_word)
        return result

    @staticmethod
    def split_to_words(words: list[str]) -> list[str]:
        result: list[str] = []
        for possible_word in words:
            for word in possible_word.split(" "):
                if word == "":
                    continue
                if word not in result:
                    result.append(word)
        return result


class NearestKeywordsForProductAPI(CalculationRequestAPI, KeywordsAPI):
    NEAREST_KEYWORDS_URL_PART = "/nearest-keywords-for-product"

    router = CalculationRequestAPI._router()
    router.prefix += NEAREST_KEYWORDS_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=list[str])
    def calculate(request_data: ProductKeywordsRequestModel,
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)) -> list[str]:
        session_controller = session_controller_depend(session)
        user = AllProductCalculateAPI.check_and_get_user(session_controller, access_token)
        user_market_data_provider = JDUClassesFactory.create_user_market_data_provider(session,
                                                                                       request_data.marketplace_id,
                                                                                       user.user_id)
        marketplace_id = request_data.marketplace_id
        product_ids = [request_data.product_id]
        filtered_user_products = extract_filtered_user_products_with_history(marketplace_id, user.user_id,
                                                                             session_controller, product_ids)
        product = filtered_user_products[request_data.product_id]
        selected_words = NearestKeywordsForProductAPI.__get_product_words(product)
        selected_words = KeywordsAPI.split_to_words(words=selected_words)
        selected_word_to_words = KeywordsAPI.get_nearest_keywords(selected_words, user_market_data_provider)
        sorted_words = []
        for word in selected_words:
            sorted_words.extend(CalculationController.sort_keywords(word, selected_word_to_words[word]))
        return sorted_words
    
    @staticmethod
    def __get_product_words(product: Product) -> list[str]:
        result = [product.name]
        for category_niche in product.category_niche_list:
            result.append(category_niche[0])
            result.append(category_niche[1])
        return result


class NearestKeywordsAPI(CalculationRequestAPI, KeywordsAPI):
    NEAREST_KEYWORDS_URL_PART = "/nearest-keywords"

    router = CalculationRequestAPI._router()
    router.prefix += NEAREST_KEYWORDS_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=list[str])
    def calculate(request_data: KeywordsRequestModel,
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)) -> list[str]:
        session_controller = session_controller_depend(session)
        user = AllProductCalculateAPI.check_and_get_user(session_controller, access_token)
        user_market_data_provider = JDUClassesFactory.create_user_market_data_provider(session,
                                                                                       request_data.marketplace_id,
                                                                                       user.user_id)
        selected_words = KeywordsAPI.split_to_words(words=request_data.sentence.split(" "))
        selected_word_to_words = KeywordsAPI.get_nearest_keywords(selected_words, user_market_data_provider)
        sorted_words = []
        for word in selected_words:
            sorted_words.extend(CalculationController.sort_keywords(word, selected_word_to_words[word]))
        return sorted_words
