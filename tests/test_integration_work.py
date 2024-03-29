import json
import os
import unittest

from jarvis_db.factories.services import create_user_items_service
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.person import User, Account
from jorm.support.constants import DEFAULT_NICHE_NAME, DEFAULT_MARKETPLACE_NAME, DEFAULT_CATEGORY_NAME, \
    DEFAULT_WAREHOUSE_NAME
from starlette.exceptions import HTTPException

from jarvis_backend.app.auth_api import SessionAPI
from jarvis_backend.app.calc.economy_analyze_api import SimpleEconomyAnalyzeAPI, TransitEconomyAnalyzeAPI
from jarvis_backend.app.calc.niche_analyze_api import NicheCharacteristicsAPI, GreenTradeZoneAPI
from jarvis_backend.app.calc.product_analyze_api import ProductDownturnAPI, ProductTurnoverAPI, AllProductCalculateAPI
from jarvis_backend.app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from jarvis_backend.app.info_api import InfoAPI
from jarvis_backend.app.tokens.token_api import TokenAPI
from jarvis_backend.app.user_api import UserAPI
from jarvis_backend.auth import TokenController
from jarvis_backend.sessions.dependencies import session_controller_depend
from jarvis_backend.sessions.exceptions import JarvisExceptionsCode
from jarvis_backend.sessions.request_items import AuthenticationModel, RegistrationModel, SimpleEconomyRequestModel, \
    SimpleEconomySaveModel, NicheRequest, NicheCharacteristicsResultModel, \
    BasicDeleteRequestModel, GetAllCategoriesModel, GetAllNichesModel, \
    GetAllMarketplacesModel, GetAllProductsModel, ProductRequestModelWithMarketplaceId, AddApiKeyModel, \
    GreenTradeZoneCalculateResultModel, BasicMarketplaceInfoModel, TransitEconomyRequestModel, TransitEconomySaveModel
from tests.basic import BasicServerTest
from tests.dependencies import db_context_depends, _get_session

if os.path.exists('test.db'):
    os.remove('test.db')

_TEST_USER_PRODUCTS = [1, 10, 77]


class IntegrationTest(BasicServerTest):
    access_token = ""
    update_token = ""
    imprint_token = ""
    session: any

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
    default_reg_item = RegistrationModel.model_validate(registration_object)
    default_auth_item_with_email = AuthenticationModel.model_validate(authentication_by_email_object)
    default_auth_item_with_phone = AuthenticationModel.model_validate(authentication_by_phone_object)

    second_registration_object = {
        "email": "anyAn@mail.com",
        "password": "MyPass12345678!",
        "phone": ""
    }
    second_authentication_by_email_object = {
        "login": "anyAn@mail.com",
        "password": "MyPass12345678!",
    }
    second_reg_item = RegistrationModel.model_validate(second_registration_object)
    second_auth_item_with_email = AuthenticationModel.model_validate(second_authentication_by_email_object)

    user: User = None

    def setUp(self) -> None:
        db_context = db_context_depends()
        self.session = _get_session(db_context)
        # Registration
        try:
            SessionAPI.registrate_user(self.default_reg_item, self.session)
            SessionAPI.registrate_user(self.second_reg_item, self.session)
        except HTTPException as e:
            print(e)
        account_service = JDBServiceFactory.create_account_service(self.session)
        found_info: tuple[Account, int] = account_service.find_by_email_or_phone(self.default_reg_item.email,
                                                                                 self.default_reg_item.phone)
        self.user, user_id = JDBServiceFactory.create_user_service(self.session).find_by_account_id(found_info[1])
        user_items_service = create_user_items_service(self.session)
        fetched_products = user_items_service.fetch_user_products(user_id, 2)
        for product_id in _TEST_USER_PRODUCTS:
            if product_id + 604 not in fetched_products:
                user_items_service.append_product(user_id, product_id + 604)  # to get second MP products
        # Authorization by email
        self.assertAuthentication(auth_item=self.default_auth_item_with_email, session=self.session)
        self.access_token, self.update_token, self.imprint_token = \
            self.assertAuthentication(self.default_auth_item_with_phone, self.session)

    def tearDown(self) -> None:
        # Logout
        response = SessionAPI.log_out(self.access_token, self.imprint_token, self.session)
        self.session.commit()
        self.session.close()
        self.assertIsNotNone(response)

    def assertAuthentication(self, auth_item, session,
                             imprint_token: str | None = None) -> tuple[str, str, str]:
        response = SessionAPI.authenticate_user(request_data=auth_item, imprint_token=imprint_token, session=session)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)
        self.assertTrue(IMPRINT_TOKEN_NAME in response_dict)
        return response_dict[ACCESS_TOKEN_NAME], response_dict[UPDATE_TOKEN_NAME], response_dict[IMPRINT_TOKEN_NAME]

    def assertTokenCorrectness(self, access_token: str):
        request_data = self.create_get_all_products_request_object(1)
        UserAPI.get_all_in_marketplace_user_products(request_data, access_token, session=self.session)

    @staticmethod
    def create_product_with_mp_id_request_object(marketplace_id: int, product_ids: list[int] = None) \
            -> ProductRequestModelWithMarketplaceId:
        if product_ids is None:
            product_ids = []
        request_data = {
            "product_ids": product_ids,
            "marketplace_id": marketplace_id
        }
        return ProductRequestModelWithMarketplaceId.model_validate(request_data)

    @staticmethod
    def create_get_all_products_request_object(marketplace_id: int) -> GetAllProductsModel:
        request_data = {
            "marketplace_id": marketplace_id
        }
        return GetAllProductsModel.model_validate(request_data)

    @staticmethod
    def create_delete_request_object(request_id: int) -> BasicDeleteRequestModel:
        request_data = {
            "request_id": request_id
        }
        return BasicDeleteRequestModel.model_validate(request_data)

    @staticmethod
    def create_get_all_marketplaces_object(is_allow_defaults: bool = False) -> GetAllMarketplacesModel:
        request_data = {
            "is_allow_defaults": is_allow_defaults
        }
        return GetAllMarketplacesModel.model_validate(request_data)

    @staticmethod
    def create_get_all_categories_object(marketplace_id: int,
                                         is_allow_defaults: bool = False) -> GetAllCategoriesModel:
        request_data = {
            "marketplace_id": marketplace_id,
            "is_allow_defaults": is_allow_defaults
        }
        return GetAllCategoriesModel.model_validate(request_data)

    @staticmethod
    def create_get_all_niches_object(category_id: int, is_allow_defaults: bool = False) -> GetAllNichesModel:
        request_data = {
            "category_id": category_id,
            "is_allow_defaults": is_allow_defaults
        }
        return GetAllNichesModel.model_validate(request_data)

    @staticmethod
    def create_basic_marketplace_info_object(marketplace_id: int) -> BasicMarketplaceInfoModel:
        request_data = {
            "marketplace_id": marketplace_id
        }
        return BasicMarketplaceInfoModel.model_validate(request_data)

    @staticmethod
    def create_add_api_key_object(marketplace_id: int, api_key: str) -> AddApiKeyModel:
        request_data = {
            "marketplace_id": marketplace_id,
            "api_key": api_key
        }
        return AddApiKeyModel.model_validate(request_data)

    def test_existing_registration(self):
        with self.assertRaises(HTTPException) as catcher:
            SessionAPI.registrate_user(self.default_reg_item, self.session)
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
        reg_item = RegistrationModel.model_validate(registration_object)
        auth_item_with_email = AuthenticationModel.model_validate(authentication_by_email_object)
        auth_item_with_phone = AuthenticationModel.model_validate(authentication_by_phone_object)
        try:
            SessionAPI.registrate_user(reg_item, self.session)
        except HTTPException:
            pass

        # Authorization by email
        self.assertAuthentication(auth_item_with_email, self.session)
        with self.assertRaises(HTTPException) as catcher:
            self.assertAuthentication(auth_item_with_phone, self.session)
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
        reg_item = RegistrationModel.model_validate(registration_object)
        auth_item_with_email = AuthenticationModel.model_validate(authentication_by_email_object)
        auth_item_with_phone = AuthenticationModel.model_validate(authentication_by_phone_object)
        try:
            SessionAPI.registrate_user(reg_item, self.session)
        except HTTPException:
            pass

        # Authorization by email
        self.assertAuthentication(auth_item_with_phone, self.session)
        with self.assertRaises(HTTPException) as catcher:
            self.assertAuthentication(auth_item_with_email, self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, catcher.exception)

    def test_registration_with_empty_login_fields(self):
        registration_object = {
            "email": "",
            "password": "MyPass1234!",
            "phone": ""
        }
        reg_item = RegistrationModel.model_validate(registration_object)
        with self.assertRaises(HTTPException) as catcher:
            SessionAPI.registrate_user(reg_item, self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, catcher.exception)

    def test_auth_with_empty_imprint_token(self):
        self.assertAuthentication(self.default_auth_item_with_email, self.session)

    def test_account_switching(self):
        access_token, update_token, imprint_token = self.assertAuthentication(self.second_auth_item_with_email,
                                                                              self.session)
        self.assertTokenCorrectness(access_token)
        access_token, update_token, imprint_token = self.assertAuthentication(self.default_auth_item_with_email,
                                                                              self.session)
        self.assertTokenCorrectness(access_token)

    def test_account_switching_with_same_imprint(self):
        access_token, update_token, self.imprint_token = self.assertAuthentication(self.second_auth_item_with_email,
                                                                                   self.session)
        SessionAPI.auth_by_token(access_token, self.imprint_token)
        access_token, update_token, self.imprint_token = self.assertAuthentication(self.default_auth_item_with_email,
                                                                                   self.session,
                                                                                   imprint_token=self.imprint_token)
        SessionAPI.auth_by_token(access_token, self.imprint_token)

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
        reg_item = RegistrationModel.model_validate(registration_object)
        auth_item_with_email = AuthenticationModel.model_validate(authentication_by_email_object)
        try:
            SessionAPI.registrate_user(reg_item, self.session)
        except HTTPException:
            pass

        access_token, update_token, imprint_token = self.assertAuthentication(auth_item_with_email,
                                                                              self.session)
        UserAPI.delete_account(access_token, self.session)
        with self.assertRaises(HTTPException) as catcher:
            SessionAPI.authenticate_user(request_data=auth_item_with_email,
                                         imprint_token=imprint_token, session=self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_LOGIN_OR_PASSWORD, catcher.exception)

    def test_work_with_tokens(self):
        # Auth with token using
        response = SessionAPI.auth_by_token(self.access_token, self.imprint_token)
        self.assertTrue(response)

        # Try to update tokens
        response = TokenAPI.update_tokens(self.update_token, self.session)
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
                                                            self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

    def test_incorrect_encoded_token(self):
        incorrect_access_token = TokenController().create_access_token(456)
        with self.assertRaises(HTTPException) as catcher:
            request_data = self.create_product_with_mp_id_request_object(2)
            ProductTurnoverAPI.calculate_all_in_marketplace(request_data, incorrect_access_token,
                                                            self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

    def test_token_correctness_check(self):
        session_controller = session_controller_depend(session=self.session)
        self.assertTrue(session_controller.check_token_correctness(self.access_token, self.imprint_token))
        self.assertTrue(session_controller.check_token_correctness(self.update_token, self.imprint_token))
        token_controller = TokenController()
        with self.assertRaises(HTTPException) as catcher:
            incorrect_access_token = token_controller.create_access_token(456)
            session_controller.check_token_correctness(incorrect_access_token, self.imprint_token)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)
        with self.assertRaises(HTTPException) as catcher:
            incorrect_update_token = token_controller.create_update_token(456)
            session_controller.check_token_correctness(incorrect_update_token, self.imprint_token)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

        decoded = token_controller.decode_data(self.access_token)
        decoded.pop("r")
        access_token_with_interrupted_random_part = \
            token_controller.create_basic_token(decoded, add_random_part=True, length_of_rand_part=60)
        self.assertFalse(
            session_controller.check_token_correctness(
                access_token_with_interrupted_random_part,
                self.imprint_token
            )
        )

    def test_token_update_with_incorrect_update_token(self):
        incorrect_update_token = TokenController().create_update_token(456)
        with self.assertRaises(HTTPException) as catcher:
            TokenAPI.update_tokens(incorrect_update_token, self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_TOKEN, catcher.exception)

    def test_simple_economy_request(self):
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        marketplace_id = 1
        niche_service = JDBServiceFactory.create_niche_service(self.session)
        found = niche_service.find_by_name(niche_name, category_id=category_id)
        self.assertIsNotNone(found)
        niche_id = found[1]

        warehouse_service = JDBServiceFactory.create_warehouse_service(self.session)
        found = warehouse_service.find_warehouse_by_name(DEFAULT_WAREHOUSE_NAME, marketplace_id)
        self.assertIsNotNone(found)
        warehouse_id = found[1]

        simple_economy_object = {
            "marketplace_id": marketplace_id,
            "niche_id": niche_id,
            "product_exist_cost": 200_00,
            "cost_price": 75_00,
            "length": 10,
            "width": 5,
            "height": 2,
            "mass": 1,
            "target_warehouse_id": warehouse_id
        }
        request_object = SimpleEconomyRequestModel.model_validate(simple_economy_object)
        calculation_result = SimpleEconomyAnalyzeAPI.calculate(
            request_data=request_object,
            access_token=self.access_token,
            session=self.session
        )
        save_object = {
            "user_result": [request_object, calculation_result[0]],
            "recommended_result": [request_object, calculation_result[1]]
        }
        simple_economy_save_item = SimpleEconomySaveModel.model_validate(save_object)
        SimpleEconomyAnalyzeAPI.save(request_data=simple_economy_save_item, access_token=self.access_token,
                                     session=self.session)
        result = SimpleEconomyAnalyzeAPI.get_all(access_token=self.access_token, session=self.session)

        self.assertEqual(1, len(result))
        saved_object = result[0]
        self.assertEqual(simple_economy_save_item.user_result, saved_object.user_result)
        self.assertEqual(simple_economy_save_item.recommended_result, saved_object.recommended_result)

        delete_request_data = self.create_delete_request_object(1)
        SimpleEconomyAnalyzeAPI.delete(request_data=delete_request_data, access_token=self.access_token,
                                       session=self.session)
        result = SimpleEconomyAnalyzeAPI.get_all(access_token=self.access_token, session=self.session)
        self.assertEqual(0, len(result))

    def test_simple_economy_request_with_invalid_niche(self):
        marketplace_id = 1
        simple_economy_object = {
            "marketplace_id": marketplace_id,
            "niche_id": 123456789,
            "product_exist_cost": 200_00,
            "cost_price": 75_00,
            "length": 10,
            "width": 5,
            "height": 2,
            "mass": 1,
            "target_warehouse_id": 1
        }
        request_object = SimpleEconomyRequestModel.model_validate(simple_economy_object)
        with self.assertRaises(HTTPException) as catcher:
            SimpleEconomyAnalyzeAPI.calculate(
                request_data=request_object,
                access_token=self.access_token,
                session=self.session
            )
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_NICHE, catcher.exception)

    def test_transit_economy_request(self):
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        marketplace_id = 1
        niche_service = JDBServiceFactory.create_niche_service(self.session)
        found = niche_service.find_by_name(niche_name, category_id=category_id)
        niche_id = found[1]

        warehouse_service = JDBServiceFactory.create_warehouse_service(self.session)
        found = warehouse_service.find_warehouse_by_name(DEFAULT_WAREHOUSE_NAME, marketplace_id)
        self.assertIsNotNone(found)
        warehouse_id = found[1]
        transit_economy_object = {
            "marketplace_id": marketplace_id,
            "niche_id": niche_id,
            "category_id": category_id,
            "product_exist_cost": 200_00,
            "cost_price": 75_00,
            "length": 10,
            "width": 5,
            "height": 2,
            "mass": 1,
            "target_warehouse_id": warehouse_id,
            "logistic_price": 2000_00,
            "logistic_count": 100,
            "transit_cost_for_cubic_meter": 20_00
        }
        request_object = TransitEconomyRequestModel.model_validate(transit_economy_object)
        calculation_result = TransitEconomyAnalyzeAPI.calculate(
            request_data=request_object,
            access_token=self.access_token,
            session=self.session
        )
        save_object = {
            "user_result": [request_object, calculation_result[0]],
            "recommended_result": [request_object, calculation_result[1]]
        }
        transit_economy_save_item = TransitEconomySaveModel.model_validate(save_object)
        TransitEconomyAnalyzeAPI.save(request_data=transit_economy_save_item, access_token=self.access_token,
                                      session=self.session)
        result = TransitEconomyAnalyzeAPI.get_all(access_token=self.access_token, session=self.session)

        self.assertEqual(1, len(result))
        saved_object = result[0]
        self.assertEqual(transit_economy_save_item.user_result, saved_object.user_result)
        self.assertEqual(transit_economy_save_item.recommended_result, saved_object.recommended_result)

        delete_request_data = self.create_delete_request_object(1)
        TransitEconomyAnalyzeAPI.delete(request_data=delete_request_data, access_token=self.access_token,
                                        session=self.session)
        result = TransitEconomyAnalyzeAPI.get_all(access_token=self.access_token, session=self.session)
        self.assertEqual(0, len(result))

    def test_transit_economy_request_with_invalid_niche(self):
        category_id: int = 1
        marketplace_id = 1
        simple_economy_object = {
            "marketplace_id": marketplace_id,
            "niche_id": 123456789,
            "category_id": category_id,
            "product_exist_cost": 200_00,
            "cost_price": 75_00,
            "length": 10,
            "width": 5,
            "height": 2,
            "mass": 1,
            "target_warehouse_id": 1,
            "logistic_price": 2000_00,
            "logistic_count": 100,
            "transit_cost_for_cubic_meter": 20_00
        }
        request_object = TransitEconomyRequestModel.model_validate(simple_economy_object)
        with self.assertRaises(HTTPException) as catcher:
            TransitEconomyAnalyzeAPI.calculate(
                request_data=request_object,
                access_token=self.access_token,
                session=self.session
            )
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_NICHE, catcher.exception)

    def test_niche_characteristics_request(self):
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        marketplace_id = 1
        niche_service = JDBServiceFactory.create_niche_service(self.session)
        found = niche_service.find_by_name(niche_name, category_id=category_id)
        self.assertIsNotNone(found)
        niche_request_object = {
            "niche_id": found[1],
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = NicheRequest.model_validate(niche_request_object)
        calculation_result = NicheCharacteristicsAPI.calculate(
            request_object,
            self.access_token, self.session
        )
        expected_result = {
            "card_count": 604,
            "niche_profit": 408619572,
            "card_trade_count": 2629,
            "mean_card_rating": 4.0,
            "card_with_trades_count": 538,
            "daily_mean_niche_profit": 13620652,
            "daily_mean_trade_count": 87,
            "mean_traded_card_cost": 155427,
            "month_mean_niche_profit_per_card": 676522,
            "monopoly_percent": 0.0,
            "maximum_profit_idx": 0,
        }
        expected_response = NicheCharacteristicsResultModel.model_validate(expected_result)
        self.assertEqual(expected_response, calculation_result)

    def test_green_trade_zone_request(self):
        niche_service = JDBServiceFactory.create_niche_service(self.session)
        niche_name: str = DEFAULT_NICHE_NAME
        category_id: int = 1
        marketplace_id = 1
        found = niche_service.find_by_name(niche_name, category_id=category_id)
        self.assertIsNotNone(found)
        niche_request_object = {
            "niche_id": found[1],
            "category_id": category_id,
            "marketplace_id": marketplace_id
        }
        request_object = NicheRequest.model_validate(niche_request_object)
        calculation_result = GreenTradeZoneAPI.calculate(
            request_object,
            self.access_token, self.session
        )
        expected_result = {
            "frequencies": [513, 59, 16, 9, 4, 1, 0, 1, 0, 1],
            "segments": [(14859, 273953), (273953, 533047), (533047, 792141), (792141, 1051235), (1051235, 1310329),
                         (1310329, 1569423), (1569423, 1828517), (1828517, 2087611), (2087611, 2346705),
                         (2346705, 2605800)],
            "best_segment_idx": 0,
            "segment_profits": [331072702, 16878704, 21960499, 28052600, 0, 0, 0, 4103700, 3945400, 2605800],
            "best_segment_profit_idx": 0,
            "mean_segment_profit": [645365, 286079, 1372531, 3116955, 0, 0, 0, 4103700, 0, 2605800],
            "best_mean_segment_profit_idx": 7,
            "mean_product_profit": [653003, 1205621, 3660083, 3506575, 0, 0, 0, 4103700, 3945400, 2605800],
            "best_mean_product_profit_idx": 7,
            "segment_product_count": [513, 59, 16, 9, 4, 1, 0, 1, 0, 1],
            "best_segment_product_count_idx": 6,
            "segment_product_with_trades_count": [507, 14, 6, 8, 0, 0, 0, 1, 1, 1],
            "best_segment_product_with_trades_count_idx": 0
        }
        expected_response = GreenTradeZoneCalculateResultModel.model_validate(expected_result)
        self.assertEqual(expected_response, calculation_result)

    def test_all_in_marketplace_product_downturn_request(self):
        request_data = self.create_product_with_mp_id_request_object(2)
        calculation_result = ProductDownturnAPI.calculate_all_in_marketplace(request_data,
                                                                             self.access_token,
                                                                             self.session)
        self.assertIsNotNone(calculation_result)
        expected_result = ("{605: SingleDownturnResult(downturn_info={1: {'second': DownturnInfoModel(leftover=14, "
                           "days=2)}}), 614: SingleDownturnResult(downturn_info={1: {'second': DownturnInfoModel("
                           "leftover=14, days=2)}}), 681: SingleDownturnResult(downturn_info={1: {'second': "
                           "DownturnInfoModel(leftover=13, days=2)}})}")  # TODO make it normal...
        self.assertEqual(expected_result, str(calculation_result.result_dict))

    def test_product_downturn_request(self):
        calculation_result = ProductDownturnAPI.calculate(access_token=self.access_token,
                                                          session=self.session)
        self.assertIsNotNone(calculation_result)
        self.assertTrue(2 in calculation_result)
        expected_result = ("{605: SingleDownturnResult(downturn_info={1: {'second': DownturnInfoModel(leftover=14, "
                           "days=2)}}), 614: SingleDownturnResult(downturn_info={1: {'second': DownturnInfoModel("
                           "leftover=14, days=2)}}), 681: SingleDownturnResult(downturn_info={1: {'second': "
                           "DownturnInfoModel(leftover=13, days=2)}})}")
        self.assertEqual(expected_result, str(calculation_result[2].result_dict))

    def test_all_in_marketplace_product_turnover_request(self):
        request_data = self.create_product_with_mp_id_request_object(2)
        calculation_result = ProductTurnoverAPI.calculate_all_in_marketplace(request_data,
                                                                             self.access_token,
                                                                             self.session)
        self.assertIsNotNone(calculation_result)
        expected_result = {
            605: {1: {'second': 99.0}},
            614: {1: {'second': 99.0}},
            681: {1: {'second': 93.0}}
        }
        self.assertEqual(expected_result, calculation_result.result_dict)

    def test_product_turnover_request_with_none_data(self):
        calculation_result = ProductTurnoverAPI.calculate(access_token=self.access_token,
                                                          session=self.session)
        self.assertIsNotNone(calculation_result)
        self.assertTrue(2 in calculation_result)
        expected_result = {
            605: {1: {'second': 99.0}},
            614: {1: {'second': 99.0}},
            681: {1: {'second': 93.0}}
        }
        self.assertEqual(expected_result, calculation_result[2].result_dict)

    def test_all_in_marketplace_product_calculation_request(self):
        request_data = self.create_product_with_mp_id_request_object(2)
        calculation_result = AllProductCalculateAPI.calculate_all_in_marketplace(request_data,
                                                                                 self.access_token,
                                                                                 self.session)
        self.assertIsNotNone(calculation_result)
        downturn_result = calculation_result.downturn
        expected_downturns = ("result_dict={605: SingleDownturnResult(downturn_info={1: {'second': DownturnInfoModel("
                              "leftover=14, days=2)}}), 614: SingleDownturnResult(downturn_info={1: {'second': "
                              "DownturnInfoModel(leftover=14, days=2)}}), 681: SingleDownturnResult(downturn_info={1: "
                              "{'second': DownturnInfoModel(leftover=13, days=2)}})}")  # TODO make it normal...
        self.assertEqual(expected_downturns, str(downturn_result))
        turnover_result = calculation_result.turnover
        expected_turnovers = {
            605: {1: {'second': 99.0}},
            614: {1: {'second': 99.0}},
            681: {1: {'second': 93.0}}
        }
        self.assertEqual(expected_turnovers, turnover_result.result_dict)

    def test_all_product_calculation_request(self):
        calculation_result = AllProductCalculateAPI.calculate(access_token=self.access_token,
                                                              session=self.session)
        self.assertIsNotNone(calculation_result)
        self.assertTrue(2 in calculation_result)
        downturn_result = calculation_result[2].downturn
        expected_downturns = ("{605: SingleDownturnResult(downturn_info={1: {'second': DownturnInfoModel(leftover=14, "
                              "days=2)}}), 614: SingleDownturnResult(downturn_info={1: {'second': DownturnInfoModel("
                              "leftover=14, days=2)}}), 681: SingleDownturnResult(downturn_info={1: {'second': "
                              "DownturnInfoModel(leftover=13, days=2)}})}")
        self.assertEqual(expected_downturns, str(downturn_result.result_dict))
        turnover_result = calculation_result[2].turnover
        expected_turnovers = {
            605: {1: {'second': 99.0}},
            614: {1: {'second': 99.0}},
            681: {1: {'second': 93.0}}
        }
        self.assertEqual(expected_turnovers, turnover_result.result_dict)

    def test_info_api_get_marketplaces_without_defaults(self):
        id_to_marketplace = InfoAPI.get_all_marketplaces(session=self.session)
        self.assertEqual({
            2: 'wildberries'
        }, id_to_marketplace)

    def test_info_api_get_marketplaces_with_defaults(self):
        request_data = self.create_get_all_marketplaces_object(is_allow_defaults=True)
        id_to_marketplace = InfoAPI.get_all_marketplaces(request_data, session=self.session)
        self.assertEqual({
            1: DEFAULT_MARKETPLACE_NAME.lower(),
            2: 'wildberries'
        }, id_to_marketplace)

    def test_info_api_get_categories_without_defaults(self):
        request_data = self.create_get_all_categories_object(1)
        id_to_category = InfoAPI.get_all_categories(request_data, session=self.session)
        self.assertEqual({}, id_to_category)

    def test_info_api_get_categories_with_defaults(self):
        request_data = self.create_get_all_categories_object(1, is_allow_defaults=True)
        id_to_category = InfoAPI.get_all_categories(request_data, session=self.session)
        self.assertEqual({
            1: DEFAULT_CATEGORY_NAME
        }, id_to_category)

    def test_info_api_get_niches_without_defaults(self):
        request_data = self.create_get_all_niches_object(1)
        id_to_niche = InfoAPI.get_all_niches(request_data, session=self.session)
        self.assertEqual({}, id_to_niche)

    def test_info_api_get_niches_with_defaults(self):
        request_data = self.create_get_all_niches_object(1, is_allow_defaults=True)
        id_to_niche = InfoAPI.get_all_niches(request_data, session=self.session)
        self.assertEqual({
            1: DEFAULT_NICHE_NAME
        }, id_to_niche)

    def test_info_api_get_all_in_marketplace_user_products(self):
        request_data = self.create_get_all_products_request_object(1)
        id_to_user_products = UserAPI.get_all_in_marketplace_user_products(request_data,
                                                                           self.access_token,
                                                                           session=self.session)
        self.assertEqual({}, id_to_user_products)

    def test_info_api_get_all_user_products(self):
        id_to_user_products = UserAPI.get_all_user_products(access_token=self.access_token,
                                                            session=self.session)
        self.assertTrue(2 in id_to_user_products)
        self.assertEqual(3, len(id_to_user_products[2]))

    def test_user_api_key_addition_into_default_marketplace(self):
        request_data = self.create_add_api_key_object(marketplace_id=1, api_key="myFirstKey")
        with self.assertRaises(HTTPException) as catcher:
            UserAPI.add_marketplace_api_key(request_data=request_data,
                                            access_token=self.access_token,
                                            session=self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_MARKETPLACE, catcher.exception)

    def test_user_api_key_addition_into_not_existed_marketplace(self):
        request_data = self.create_add_api_key_object(marketplace_id=8579, api_key="myFirstKey")
        with self.assertRaises(HTTPException) as catcher:
            UserAPI.add_marketplace_api_key(request_data=request_data,
                                            access_token=self.access_token,
                                            session=self.session)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.INCORRECT_MARKETPLACE, catcher.exception)


if __name__ == '__main__':
    unittest.main()
