import datetime
import json
import os
import unittest

from jarvis_db.factories.services import create_user_items_service
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.person import User, Account
from jorm.market.service import UnitEconomyResult, FrequencyResult
from jorm.support.constants import DEFAULT_NICHE_NAME, DEFAULT_MARKETPLACE_NAME, DEFAULT_CATEGORY_NAME
from starlette.exceptions import HTTPException

from jarvis_backend.app.auth_api import SessionAPI
from jarvis_backend.app.calc.economy_analyze_api import EconomyAnalyzeAPI
from jarvis_backend.app.calc.niche_analyze_api import NicheFrequencyAPI, NicheCharacteristicsAPI, GreenTradeZoneAPI
from jarvis_backend.app.calc.product_analyze_api import ProductDownturnAPI, ProductTurnoverAPI, AllProductCalculateAPI
from jarvis_backend.app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from jarvis_backend.app.info_api import InfoAPI
from jarvis_backend.app.tokens.token_api import TokenAPI
from jarvis_backend.app.user_api import UserAPI
from jarvis_backend.auth import TokenController
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend, \
    request_handler_depend
from jarvis_backend.sessions.exceptions import JarvisExceptionsCode
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.sessions.request_items import AuthenticationObject, RegistrationObject, UnitEconomyRequestObject, \
    UnitEconomySaveObject, FrequencyRequest, FrequencySaveObject, NicheRequest, NicheCharacteristicsResultObject, \
    RequestInfo, BasicDeleteRequestObject, GetAllCategoriesObject, GetAllNichesObject, \
    GetAllMarketplacesObject, GetAllProductsObject, ProductRequestObjectWithMarketplaceId, AddApiKeyObject, \
    GreenTradeZoneCalculateResultObject, BasicMarketplaceInfoObject
from jarvis_backend.support.utils import pydantic_to_jorm
from tests.basic import BasicServerTest
from tests.dependencies import db_context_depends, _get_session

if os.path.exists('test.db'):
    os.remove('test.db')

_TEST_USER_PRODUCTS = [1, 10, 77, 85, 102, 145, 204, 345]


class IntegrationTest(BasicServerTest):
    access_token = ""
    update_token = ""
    imprint_token = ""
    session_controller: JarvisSessionController
    session: any
    request_handler: RequestHandler

    registration_object = {
        "email": "any@mail.com",
        "password": "MyPass1234!",
        "phone": "+16034134121"
    }
    authentication_by_email_object = {
        "login": "any@mail.com",
        "password": "MyPass1234!",
    }
    authentication_by_phone_object = {
        "login": "+16034134121",
        "password": "MyPass1234!",
    }
    default_reg_item = RegistrationObject.model_validate(registration_object)
    default_auth_item_with_email = AuthenticationObject.model_validate(authentication_by_email_object)
    default_auth_item_with_phone = AuthenticationObject.model_validate(authentication_by_phone_object)
    user: User = None

    def setUp(self) -> None:
        db_context = db_context_depends()
        self.session = _get_session(db_context)
        self.session_controller = session_controller_depend(self.session)
        self.request_handler = request_handler_depend(self.session)
        # Registration
        try:
            SessionAPI.registrate_user(self.default_reg_item, self.session_controller)
        except HTTPException as e:
            print(e)
        account_service = JDBServiceFactory.create_account_service(self.session)
        found_info: tuple[Account, int] = account_service.find_by_email_or_phone(self.default_reg_item.email,
                                                                                 self.default_reg_item.phone)
        self.user, user_id = JDBServiceFactory.create_user_service(self.session).find_by_account_id(found_info[1])
        user_items_service = create_user_items_service(self.session)
        fetched_products = user_items_service.fetch_user_products(user_id)
        for product_id in _TEST_USER_PRODUCTS:
            if product_id not in fetched_products:
                user_items_service.append_product(user_id, product_id)
        # Authorization by email
        self.assertAuthentication(self.default_auth_item_with_email, self.session_controller)
        self.access_token, self.update_token, self.imprint_token = \
            self.assertAuthentication(self.default_auth_item_with_phone, self.session_controller)

    def tearDown(self) -> None:
        # Logout
        response = SessionAPI.log_out(self.access_token, self.imprint_token, self.session_controller)
        self.session.commit()
        self.session.close()
        self.assertIsNotNone(response)

    def assertAuthentication(self, auth_item, session_controller,
                             imprint_token: str | None = None) -> tuple[str, str, str]:
        response = SessionAPI.authenticate_user(auth_item, imprint_token, session_controller)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)
        self.assertTrue(IMPRINT_TOKEN_NAME in response_dict)
        return response_dict[ACCESS_TOKEN_NAME], response_dict[UPDATE_TOKEN_NAME], response_dict[IMPRINT_TOKEN_NAME]

    @staticmethod
    def create_product_with_mp_id_request_object(marketplace_id: int, product_ids: list[int] = None) \
            -> ProductRequestObjectWithMarketplaceId:
        if product_ids is None:
            product_ids = []
        request_data = {
            "product_ids": product_ids,
            "marketplace_id": marketplace_id
        }
        return ProductRequestObjectWithMarketplaceId.model_validate(request_data)

    @staticmethod
    def create_get_all_products_request_object(marketplace_id: int) -> GetAllProductsObject:
        request_data = {
            "marketplace_id": marketplace_id
        }
        return GetAllProductsObject.model_validate(request_data)

    @staticmethod
    def create_delete_request_object(request_id: int) -> BasicDeleteRequestObject:
        request_data = {
            "request_id": request_id
        }
        return BasicDeleteRequestObject.model_validate(request_data)

    @staticmethod
    def create_get_all_marketplaces_object(is_allow_defaults: bool = False) -> GetAllMarketplacesObject:
        request_data = {
            "is_allow_defaults": is_allow_defaults
        }
        return GetAllMarketplacesObject.model_validate(request_data)

    @staticmethod
    def create_get_all_categories_object(marketplace_id: int,
                                         is_allow_defaults: bool = False) -> GetAllCategoriesObject:
        request_data = {
            "marketplace_id": marketplace_id,
            "is_allow_defaults": is_allow_defaults
        }
        return GetAllCategoriesObject.model_validate(request_data)

    @staticmethod
    def create_get_all_niches_object(category_id: int, is_allow_defaults: bool = False) -> GetAllNichesObject:
        request_data = {
            "category_id": category_id,
            "is_allow_defaults": is_allow_defaults
        }
        return GetAllNichesObject.model_validate(request_data)

    @staticmethod
    def create_basic_marketplace_info_object(marketplace_id: int) -> BasicMarketplaceInfoObject:
        request_data = {
            "marketplace_id": marketplace_id
        }
        return BasicMarketplaceInfoObject.model_validate(request_data)

    @staticmethod
    def create_add_api_key_object(marketplace_id: int, api_key: str) -> AddApiKeyObject:
        request_data = {
            "marketplace_id": marketplace_id,
            "api_key": api_key
        }
        return AddApiKeyObject.model_validate(request_data)

    def test_existing_registration(self):
        with self.assertRaises(HTTPException) as catcher:
            SessionAPI.registrate_user(self.default_reg_item, self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.REGISTER_EXISTING_LOGIN, catcher.exception)

    def test_registration_and_auth_with_empty_number(self):
        registration_object = {
            "email": "anyAnother@mail.com",
            "password": "MyPass1234!",
            "phone": ""
        }
        authentication_by_email_object = {
            "login": "anyAnother@mail.com",
            "password": "MyPass1234!",
        }
        authentication_by_phone_object = {
            "login": "+79138990213",  # incorrect number
            "password": "MyPass1234!",
        }
        reg_item = RegistrationObject.model_validate(registration_object)
        auth_item_with_email = AuthenticationObject.model_validate(authentication_by_email_object)
        auth_item_with_phone = AuthenticationObject.model_validate(authentication_by_phone_object)
        try:
            SessionAPI.registrate_user(reg_item, self.session_controller)
        except HTTPException:
            pass

        # Authorization by email
        self.assertAuthentication(auth_item_with_email, self.session_controller)
        with self.assertRaises(HTTPException) as catcher:
            self.assertAuthentication(auth_item_with_phone, self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, catcher.exception)

    def test_registration_and_auth_with_empty_email(self):
        registration_object = {
            "email": "",
            "password": "MyPass1234!",
            "phone": "+79138990214"
        }
        authentication_by_email_object = {
            "login": "anyAnother@mail.com",  # incorrect email
            "password": "MyPass1234!",
        }
        authentication_by_phone_object = {
            "login": "+79138990214",
            "password": "MyPass1234!",
        }
        reg_item = RegistrationObject.model_validate(registration_object)
        auth_item_with_email = AuthenticationObject.model_validate(authentication_by_email_object)
        auth_item_with_phone = AuthenticationObject.model_validate(authentication_by_phone_object)
        try:
            SessionAPI.registrate_user(reg_item, self.session_controller)
        except HTTPException:
            pass

        # Authorization by email
        self.assertAuthentication(auth_item_with_phone, self.session_controller)
        with self.assertRaises(HTTPException) as catcher:
            self.assertAuthentication(auth_item_with_email, self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, catcher.exception)

    def test_registration_with_empty_login_fields(self):
        registration_object = {
            "email": "",
            "password": "MyPass1234!",
            "phone": ""
        }
        reg_item = RegistrationObject.model_validate(registration_object)
        with self.assertRaises(HTTPException) as catcher:
            SessionAPI.registrate_user(reg_item, self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, catcher.exception)

    def test_auth_with_empty_imprint_token(self):
        self.assertAuthentication(self.default_auth_item_with_email,
                                  self.session_controller, imprint_token=self.imprint_token)

    def test_account_deletion(self):
        registration_object = {
            "email": "anyAnotherA@mail.com",
            "password": "MyPass1234!",
            "phone": ""
        }
        authentication_by_email_object = {
            "login": "anyAnotherA@mail.com",
            "password": "MyPass1234!",
        }
        reg_item = RegistrationObject.model_validate(registration_object)
        auth_item_with_email = AuthenticationObject.model_validate(authentication_by_email_object)
        try:
            SessionAPI.registrate_user(reg_item, self.session_controller)
        except HTTPException:
            pass

        access_token, update_token, imprint_token = self.assertAuthentication(auth_item_with_email,
                                                                              self.session_controller)
        UserAPI.delete_account(access_token, self.session_controller)
        with self.assertRaises(HTTPException) as catcher:
            SessionAPI.authenticate_user(auth_item_with_email, imprint_token, self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, catcher.exception)

    def test_work_with_tokens(self):
        # Auth with token using
        response = SessionAPI.auth_by_token(self.access_token, self.imprint_token)
        self.assertTrue(response)

        # Try to update tokens
        response = TokenAPI.update_tokens(self.update_token, self.session_controller)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)

        self.access_token = response_dict[ACCESS_TOKEN_NAME]
        self.update_token = response_dict[UPDATE_TOKEN_NAME]

    def test_incorrect_token(self):
        request_data = self.create_product_with_mp_id_request_object(2)
        with self.assertRaises(HTTPException) as catcher:
            ProductTurnoverAPI.calculate_all_in_marketplace(request_data, self.access_token + "wrong",
                                                            self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

    def test_incorrect_encoded_token(self):
        incorrect_access_token = TokenController().create_access_token(456)
        with self.assertRaises(HTTPException) as catcher:
            request_data = self.create_product_with_mp_id_request_object(2)
            ProductTurnoverAPI.calculate_all_in_marketplace(request_data, incorrect_access_token,
                                                            self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

    def test_token_correctness_check(self):
        self.assertTrue(self.session_controller.check_token_correctness(self.access_token, self.imprint_token))
        self.assertTrue(self.session_controller.check_token_correctness(self.update_token, self.imprint_token))
        token_controller = TokenController()
        with self.assertRaises(HTTPException) as catcher:
            incorrect_access_token = token_controller.create_access_token(456)
            self.session_controller.check_token_correctness(incorrect_access_token, self.imprint_token)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)
        with self.assertRaises(HTTPException) as catcher:
            incorrect_update_token = token_controller.create_update_token(456)
            self.session_controller.check_token_correctness(incorrect_update_token, self.imprint_token)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

        decoded = token_controller.decode_data(self.access_token)
        decoded.pop("r")
        access_token_with_interrupted_random_part = \
            token_controller.create_basic_token(decoded, add_random_part=True, length_of_rand_part=60)
        self.assertFalse(
            self.session_controller.check_token_correctness(
                access_token_with_interrupted_random_part,
                self.imprint_token
            )
        )

    def test_token_update_with_incorrect_update_token(self):
        incorrect_update_token = TokenController().create_update_token(456)
        with self.assertRaises(HTTPException) as catcher:
            TokenAPI.update_tokens(incorrect_update_token, self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

    def test_unit_economy_request(self):
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        buy: int = 50_00
        pack: int = 50_00
        transit_price: int = 1000_00
        transit_count: int = 1000
        marketplace_transit_price: int = 1500_00
        marketplace_id = 1
        unit_economy_object = {
            "buy": buy,
            "pack": pack,
            "niche": niche_name,
            "category_id": category_id,
            "transit_count": transit_count,
            "transit_price": transit_price,
            "market_place_transit_price": marketplace_transit_price,
            "warehouse_name": "DEFAULT_WAREHOUSE",
            "marketplace_id": marketplace_id
        }
        request_object = UnitEconomyRequestObject.model_validate(unit_economy_object)
        calculation_result = EconomyAnalyzeAPI.calculate(
            request_object,
            self.access_token, self.session_controller
        )
        save_dict = {
            'request': request_object,
            'result': calculation_result
        }
        unit_economy_save_item = UnitEconomySaveObject.model_validate(save_dict)
        EconomyAnalyzeAPI.save(unit_economy_save_item, self.access_token, self.session_controller, self.request_handler)
        result = EconomyAnalyzeAPI.get_all(self.access_token, self.session_controller, self.request_handler)

        self.assertEqual(1, len(result))
        saved_object = result[0]
        self.assertEqual(buy, saved_object.request.buy)
        self.assertEqual(pack, saved_object.request.pack)
        self.assertEqual(niche_name, saved_object.request.niche)
        self.assertEqual(category_id, saved_object.request.category_id)
        self.assertEqual(transit_count, saved_object.request.transit_count)
        self.assertEqual(transit_price, saved_object.request.transit_price)
        self.assertEqual(marketplace_id, saved_object.request.marketplace_id)

        jorm_result = pydantic_to_jorm(UnitEconomyResult, calculation_result)
        self.assertEqual(jorm_result.product_cost, saved_object.result.product_cost)
        self.assertEqual(jorm_result.pack_cost, saved_object.result.product_cost)
        self.assertEqual(jorm_result.marketplace_commission, saved_object.result.marketplace_commission)
        self.assertTrue(abs(jorm_result.roi - saved_object.result.roi) <= 0.01)
        self.assertEqual(jorm_result.logistic_price, saved_object.result.logistic_price)
        self.assertEqual(jorm_result.storage_price, saved_object.result.storage_price)
        self.assertEqual(jorm_result.margin, saved_object.result.margin)
        self.assertTrue(abs(jorm_result.transit_margin - saved_object.result.transit_margin) <= 0.01)
        self.assertEqual(jorm_result.recommended_price, saved_object.result.recommended_price)
        self.assertEqual(jorm_result.transit_profit, saved_object.result.transit_profit)

        delete_request_data = self.create_delete_request_object(1)
        EconomyAnalyzeAPI.delete(delete_request_data, self.access_token, self.session_controller, self.request_handler)
        result = EconomyAnalyzeAPI.get_all(self.access_token, self.session_controller, self.request_handler)
        self.assertEqual(0, len(result))

    def test_unit_economy_request_with_non_default_niche(self):
        niche_name: str = 'хурма 16'
        category_id: int = 0
        buy: int = 50_00
        pack: int = 50_00
        transit_price: int = 1000_00
        transit_count: int = 1000
        marketplace_transit_price: int = 1500_00
        marketplace_id = 2
        unit_economy_object = {
            "buy": buy,
            "pack": pack,
            "niche": niche_name,
            "category_id": category_id,
            "transit_count": transit_count,
            "transit_price": transit_price,
            "market_place_transit_price": marketplace_transit_price,
            "warehouse_name": "DEFAULT_WAREHOUSE",
            "marketplace_id": marketplace_id
        }
        request_object = UnitEconomyRequestObject.model_validate(unit_economy_object)
        calculation_result = EconomyAnalyzeAPI.calculate(
            request_object,
            self.access_token, self.session_controller
        )
        save_dict = {
            'request': request_object,
            'result': calculation_result
        }
        unit_economy_save_item = UnitEconomySaveObject.model_validate(save_dict)
        EconomyAnalyzeAPI.save(unit_economy_save_item, self.access_token, self.session_controller, self.request_handler)
        result = EconomyAnalyzeAPI.get_all(self.access_token, self.session_controller, self.request_handler)

        self.assertEqual(1, len(result))
        saved_object = result[0]
        self.assertEqual(buy, saved_object.request.buy)
        self.assertEqual(pack, saved_object.request.pack)
        self.assertEqual(niche_name, saved_object.request.niche)
        self.assertEqual(2, saved_object.request.category_id)  # expected 2 as a default category id for WB
        self.assertEqual(transit_count, saved_object.request.transit_count)
        self.assertEqual(transit_price, saved_object.request.transit_price)
        self.assertEqual(marketplace_id, saved_object.request.marketplace_id)

        jorm_result = pydantic_to_jorm(UnitEconomyResult, calculation_result)
        self.assertEqual(jorm_result.product_cost, saved_object.result.product_cost)
        self.assertEqual(jorm_result.pack_cost, saved_object.result.product_cost)
        self.assertEqual(jorm_result.marketplace_commission, saved_object.result.marketplace_commission)
        self.assertTrue(abs(jorm_result.roi - saved_object.result.roi) <= 0.01)
        self.assertEqual(jorm_result.logistic_price, saved_object.result.logistic_price)
        self.assertEqual(jorm_result.storage_price, saved_object.result.storage_price)
        self.assertEqual(jorm_result.margin, saved_object.result.margin)
        self.assertTrue(abs(jorm_result.transit_margin - saved_object.result.transit_margin) <= 0.01)
        self.assertEqual(jorm_result.recommended_price, saved_object.result.recommended_price)
        self.assertEqual(jorm_result.transit_profit, saved_object.result.transit_profit)

        delete_request_data = self.create_delete_request_object(1)
        EconomyAnalyzeAPI.delete(delete_request_data, self.access_token, self.session_controller, self.request_handler)
        result = EconomyAnalyzeAPI.get_all(self.access_token, self.session_controller, self.request_handler)
        self.assertEqual(0, len(result))

    def test_unit_economy_request_with_invalid_niche(self):
        niche_name: str = "invalid_name3"
        category_id: int = 1
        buy: int = 50_00
        pack: int = 50_00
        transit_price: int = 1000_00
        transit_count: int = 1000
        marketplace_transit_price: int = 1500_00
        marketplace_id = 1
        unit_economy_object = {
            "buy": buy,
            "pack": pack,
            "niche": niche_name,
            "category_id": category_id,
            "transit_count": transit_count,
            "transit_price": transit_price,
            "market_place_transit_price": marketplace_transit_price,
            "warehouse_name": "DEFAULT_WAREHOUSE",
            "marketplace_id": marketplace_id
        }
        request_object = UnitEconomyRequestObject.model_validate(unit_economy_object)
        with self.assertRaises(HTTPException) as catcher:
            EconomyAnalyzeAPI.calculate(
                request_object,
                self.access_token, self.session_controller
            )
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_NICHE, catcher.exception)

    def test_frequency_request(self):
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        marketplace_id = 1
        niche_request_object = {
            "niche": niche_name,
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = FrequencyRequest.model_validate(niche_request_object)
        calculation_result = NicheFrequencyAPI.calculate(
            request_object,
            self.access_token, self.session_controller
        )
        request_info_object = RequestInfo.model_validate({
            'name': "MyRequest",
            'id': None,
            'timestamp': datetime.datetime.utcnow().timestamp()
        })
        save_dict = {
            'request': request_object,
            'result': calculation_result,
            'info': request_info_object
        }
        frequency_save_item = FrequencySaveObject.model_validate(save_dict)
        NicheFrequencyAPI.save(frequency_save_item, self.access_token, self.session_controller, self.request_handler)
        result = NicheFrequencyAPI.get_all(self.access_token, self.session_controller, self.request_handler)

        self.assertEqual(1, len(result))
        saved_object = result[0]
        self.assertEqual(request_info_object.name, saved_object.info.name)
        self.assertEqual(request_info_object.timestamp, saved_object.info.timestamp)

        self.assertEqual(niche_name, saved_object.request.niche)
        self.assertEqual(category_id, saved_object.request.category_id)
        self.assertEqual(marketplace_id, saved_object.request.marketplace_id)

        jorm_result = pydantic_to_jorm(FrequencyResult, calculation_result)
        self.assertEqual(jorm_result.x, saved_object.result.x)
        self.assertEqual(jorm_result.y, saved_object.result.y)

        delete_request_data = self.create_delete_request_object(1)
        NicheFrequencyAPI.delete(delete_request_data, self.access_token, self.session_controller, self.request_handler)
        result = NicheFrequencyAPI.get_all(self.access_token, self.session_controller, self.request_handler)
        self.assertEqual(0, len(result))

    def test_frequency_request_with_non_default_niche(self):
        niche_name: str = 'хурма 15'
        category_id: int = 0
        marketplace_id = 2
        niche_request_object = {
            "niche": niche_name,
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = FrequencyRequest.model_validate(niche_request_object)
        calculation_result = NicheFrequencyAPI.calculate(
            request_object,
            self.access_token, self.session_controller
        )
        request_info_object = RequestInfo.model_validate({
            'name': "MyRequest",
            'id': None,
            'timestamp': datetime.datetime.utcnow().timestamp()
        })
        save_dict = {
            'request': request_object,
            'result': calculation_result,
            'info': request_info_object
        }
        frequency_save_item = FrequencySaveObject.model_validate(save_dict)
        NicheFrequencyAPI.save(frequency_save_item, self.access_token, self.session_controller, self.request_handler)
        result = NicheFrequencyAPI.get_all(self.access_token, self.session_controller, self.request_handler)

        self.assertEqual(1, len(result))
        saved_object = result[0]
        self.assertEqual(request_info_object.name, saved_object.info.name)
        self.assertEqual(request_info_object.timestamp, saved_object.info.timestamp)

        self.assertEqual(niche_name, saved_object.request.niche)
        self.assertEqual(2, saved_object.request.category_id)  # expected 2 as a default category id for WB
        self.assertEqual(marketplace_id, saved_object.request.marketplace_id)

        jorm_result = pydantic_to_jorm(FrequencyResult, calculation_result)
        self.assertEqual(jorm_result.x, saved_object.result.x)
        self.assertEqual(jorm_result.y, saved_object.result.y)

        delete_request_data = self.create_delete_request_object(1)
        NicheFrequencyAPI.delete(delete_request_data, self.access_token, self.session_controller, self.request_handler)
        result = NicheFrequencyAPI.get_all(self.access_token, self.session_controller, self.request_handler)
        self.assertEqual(0, len(result))

    def test_frequency_request_with_invalid_niche(self):
        niche_name: str = "invalid_name"
        category_id: int = 1
        marketplace_id = 1
        niche_request_object = {
            "niche": niche_name,
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = FrequencyRequest.model_validate(niche_request_object)
        with self.assertRaises(HTTPException) as catcher:
            NicheFrequencyAPI.calculate(
                request_object,
                self.access_token, self.session_controller
            )
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_NICHE, catcher.exception)

    def test_niche_characteristics_request(self):
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        marketplace_id = 1
        niche_request_object = {
            "niche": niche_name,
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = NicheRequest.model_validate(niche_request_object)
        calculation_result = NicheCharacteristicsAPI.calculate(
            request_object,
            self.access_token, self.session_controller
        )
        expected_result = {
            "card_count": 604,
            "niche_profit": 1266157987,
            "card_trade_count": 8783,
            "mean_card_rating": 4.0,
            "card_with_trades_count": 538,
            "daily_mean_niche_profit": 42205266,
            "daily_mean_trade_count": 292,
            "mean_traded_card_cost": 144160,
            "month_mean_niche_profit_per_card": 2096288,
            "monopoly_percent": 0.0,
            "maximum_profit_idx": 2,
        }
        expected_response = NicheCharacteristicsResultObject.model_validate(expected_result)
        self.assertEqual(expected_response, calculation_result)

    def test_niche_characteristics_request_with_invalid_niche(self):
        niche_name: str = "invalid_name2"
        category_id: int = 1
        marketplace_id = 1
        niche_request_object = {
            "niche": niche_name,
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = NicheRequest.model_validate(niche_request_object)
        with self.assertRaises(HTTPException) as catcher:
            NicheCharacteristicsAPI.calculate(
                request_object,
                self.access_token, self.session_controller
            )
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_NICHE, catcher.exception)

    def test_green_trade_zone_request(self):
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        marketplace_id = 1
        niche_request_object = {
            "niche": niche_name,
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = NicheRequest.model_validate(niche_request_object)
        calculation_result = GreenTradeZoneAPI.calculate(
            request_object,
            self.access_token, self.session_controller
        )
        expected_result = {
            "segments": [(14859, 273953), (273953, 533047), (533047, 792141), (792141, 1051235), (1051235, 1310329),
                         (1310329, 1569423), (1569423, 1828517), (1828517, 2087611), (2087611, 2346705),
                         (2346705, 2605800)],
            "best_segment_idx": 0,
            "segment_profits": [1174263837, 19194507, 27340119, 34704500, 0, 0, 0, 4103700, 3945400, 2605800],
            "best_segment_profit_idx": 0,
            "mean_segment_profit": [2289013, 325330, 1708757, 3856055, 0, 0, 0, 4103700, 0, 2605800],
            "best_mean_segment_profit_idx": 7,
            "mean_product_profit": [2316102, 1371036, 4556686, 4338062, 0, 0, 0, 4103700, 3945400, 2605800],
            "best_mean_product_profit_idx": 2,
            "segment_product_count": [513, 59, 16, 9, 4, 1, 0, 1, 0, 1],
            "best_segment_product_count_idx": 6,
            "segment_product_with_trades_count": [507, 14, 6, 8, 0, 0, 0, 1, 1, 1],
            "best_segment_product_with_trades_count_idx": 0
        }
        expected_response = GreenTradeZoneCalculateResultObject.model_validate(expected_result)
        self.assertEqual(expected_response, calculation_result)

    def test_all_in_marketplace_product_downturn_request(self):
        # todo waiting JDB user's product save
        request_data = self.create_product_with_mp_id_request_object(2)
        calculation_result = ProductDownturnAPI.calculate_all_in_marketplace(request_data,
                                                                             self.access_token,
                                                                             self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)

    def test_product_downturn_request(self):
        # todo waiting JDB user's product save
        calculation_result = ProductDownturnAPI.calculate(access_token=self.access_token,
                                                          session_controller=self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)

    def test_all_in_marketplace_product_turnover_request(self):
        # todo waiting JDB user's product save
        request_data = self.create_product_with_mp_id_request_object(2)
        calculation_result = ProductTurnoverAPI.calculate_all_in_marketplace(request_data,
                                                                             self.access_token,
                                                                             self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)

    def test_product_turnover_request_with_none_data(self):
        # todo waiting JDB user's product save
        calculation_result = ProductTurnoverAPI.calculate(access_token=self.access_token,
                                                          session_controller=self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)

    def test_all_in_marketplace_product_calculation_request(self):
        # todo waiting JDB user's product save
        request_data = self.create_product_with_mp_id_request_object(2)
        calculation_result = AllProductCalculateAPI.calculate_all_in_marketplace(request_data,
                                                                                 self.access_token,
                                                                                 self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)

    def test_all_product_calculation_request(self):
        # todo waiting JDB user's product save
        calculation_result = AllProductCalculateAPI.calculate(access_token=self.access_token,
                                                              session_controller=self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)

    def test_info_api_get_marketplaces_without_defaults(self):
        id_to_marketplace = InfoAPI.get_all_marketplaces(session_controller=self.session_controller)
        self.assertEqual({
            2: 'wildberries'
        }, id_to_marketplace)

    def test_info_api_get_marketplaces_with_defaults(self):
        request_data = self.create_get_all_marketplaces_object(is_allow_defaults=True)
        id_to_marketplace = InfoAPI.get_all_marketplaces(request_data, session_controller=self.session_controller)
        self.assertEqual({
            1: DEFAULT_MARKETPLACE_NAME.lower(),
            2: 'wildberries'
        }, id_to_marketplace)

    def test_info_api_get_categories_without_defaults(self):
        request_data = self.create_get_all_categories_object(1)
        id_to_category = InfoAPI.get_all_categories(request_data, session_controller=self.session_controller)
        self.assertEqual({}, id_to_category)

    def test_info_api_get_categories_with_defaults(self):
        request_data = self.create_get_all_categories_object(1, is_allow_defaults=True)
        id_to_category = InfoAPI.get_all_categories(request_data, session_controller=self.session_controller)
        self.assertEqual({
            1: DEFAULT_CATEGORY_NAME
        }, id_to_category)

    def test_info_api_get_niches_without_defaults(self):
        request_data = self.create_get_all_niches_object(1)
        id_to_niche = InfoAPI.get_all_niches(request_data, session_controller=self.session_controller)
        self.assertEqual({}, id_to_niche)

    def test_info_api_get_niches_with_defaults(self):
        request_data = self.create_get_all_niches_object(1, is_allow_defaults=True)
        id_to_niche = InfoAPI.get_all_niches(request_data, session_controller=self.session_controller)
        self.assertEqual({
            1: DEFAULT_NICHE_NAME
        }, id_to_niche)

    def test_info_api_get_all_in_marketplace_user_products(self):
        request_data = self.create_get_all_products_request_object(1)
        id_to_user_products = InfoAPI.get_all_in_marketplace_user_products(request_data,
                                                                           self.access_token,
                                                                           session_controller=self.session_controller)
        self.assertEqual({}, id_to_user_products)

    def test_info_api_get_all_user_products(self):
        id_to_user_products = InfoAPI.get_all_user_products(access_token=self.access_token,
                                                            session_controller=self.session_controller)
        self.assertEqual({2: {}}, id_to_user_products)

    def test_user_api_key_working(self):
        first_key = "myFirstKey"
        request_data = self.create_add_api_key_object(marketplace_id=2, api_key=first_key)
        UserAPI.add_marketplace_api_key(request_data=request_data,
                                        access_token=self.access_token,
                                        session_controller=self.session_controller)
        saved_api_keys = UserAPI.get_all_marketplace_api_keys(access_token=self.access_token,
                                                              session_controller=self.session_controller)
        self.assertEqual(1, len(saved_api_keys))
        self.assertEqual(first_key, saved_api_keys[2])

        second_key = "mySecondKey"
        request_data = self.create_add_api_key_object(marketplace_id=2, api_key=second_key)
        with self.assertRaises(HTTPException) as catcher:
            UserAPI.add_marketplace_api_key(request_data=request_data,
                                            access_token=self.access_token,
                                            session_controller=self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.USER_FUCKS, catcher.exception)

        request_data = self.create_basic_marketplace_info_object(marketplace_id=2)
        UserAPI.delete_marketplace_api_key(request_data=request_data,
                                           access_token=self.access_token,
                                           session_controller=self.session_controller)
        saved_api_keys = UserAPI.get_all_marketplace_api_keys(access_token=self.access_token,
                                                              session_controller=self.session_controller)
        self.assertEqual(0, len(saved_api_keys))

    def test_user_api_key_addition_into_default_marketplace(self):
        request_data = self.create_add_api_key_object(marketplace_id=1, api_key="myFirstKey")
        with self.assertRaises(HTTPException) as catcher:
            UserAPI.add_marketplace_api_key(request_data=request_data,
                                            access_token=self.access_token,
                                            session_controller=self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_MARKETPLACE, catcher.exception)

    def test_user_api_key_addition_into_not_existed_marketplace(self):
        request_data = self.create_add_api_key_object(marketplace_id=8579, api_key="myFirstKey")
        with self.assertRaises(HTTPException) as catcher:
            UserAPI.add_marketplace_api_key(request_data=request_data,
                                            access_token=self.access_token,
                                            session_controller=self.session_controller)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_MARKETPLACE, catcher.exception)


if __name__ == '__main__':
    unittest.main()
