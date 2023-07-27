import json
import unittest

from jorm.market.service import UnitEconomyResult, FrequencyResult
from jorm.support.constants import DEFAULT_NICHE_NAME
from starlette.exceptions import HTTPException

from app.auth_api import SessionAPI
from app.calc.economy_analyze_api import EconomyAnalyzeAPI
from app.calc.niche_analyze_api import NicheFrequencyAPI, NicheCharacteristicsAPI
from app.calc.product_analyze_api import ProductDownturnAPI, ProductTurnoverAPI
from app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from app.tokens.token_api import TokenAPI
from sessions.controllers import JarvisSessionController
from sessions.dependencies import db_context_depends, init_defaults, session_controller_depend, request_handler_depend
from sessions.request_handler import RequestHandler
from sessions.request_items import AuthenticationObject, RegistrationObject, UnitEconomyRequestObject, \
    UnitEconomySaveObject, FrequencyRequest, FrequencySaveObject, NicheRequest
from support.utils import pydantic_to_jorm

__DEFAULTS_INITED = False


def get_session(db_context):
    global __DEFAULTS_INITED
    with db_context.session() as session, session.begin():
        if not __DEFAULTS_INITED:
            init_defaults(session)
            __DEFAULTS_INITED = True
        return session


class IntegrationTest(unittest.TestCase):
    access_token = ""
    update_token = ""
    imprint_token = ""
    session_controller: JarvisSessionController
    session: any
    request_handler: RequestHandler
    session_api = SessionAPI()
    token_api = TokenAPI()

    def assertAuthentication(self, auth_item, session_controller) -> tuple[str, str, str]:
        response = self.session_api.authenticate_user(auth_item, None, session_controller)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)
        self.assertTrue(IMPRINT_TOKEN_NAME in response_dict)
        return response_dict[ACCESS_TOKEN_NAME], response_dict[UPDATE_TOKEN_NAME], response_dict[IMPRINT_TOKEN_NAME]

    def setUp(self) -> None:
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
        reg_item = RegistrationObject.model_validate(registration_object)
        auth_item_with_email = AuthenticationObject.model_validate(authentication_by_email_object)
        auth_item_with_phone = AuthenticationObject.model_validate(authentication_by_phone_object)
        db_context = db_context_depends()
        self.session = get_session(db_context)
        self.session_controller = session_controller_depend(self.session)
        self.request_handler = request_handler_depend(self.session)
        # Registration
        try:
            self.session_api.registrate_user(reg_item, self.session_controller)
        except HTTPException:
            pass

        # Authorization by email
        self.assertAuthentication(auth_item_with_email, self.session_controller)
        self.access_token, self.update_token, self.imprint_token = \
            self.assertAuthentication(auth_item_with_phone, self.session_controller)

    def tearDown(self) -> None:
        # Logout
        response = self.session_api.log_out(self.access_token, self.imprint_token, self.session_controller)
        self.session.close()
        self.assertIsNotNone(response)

    def test_work_with_tokens(self):
        # Auth with token using
        response = self.session_api.auth_by_token(self.access_token, self.imprint_token)
        self.assertTrue(response)

        # Try to update tokens
        response = self.token_api.update_tokens(self.update_token, self.session_controller)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)

        self.access_token = response_dict[ACCESS_TOKEN_NAME]
        self.update_token = response_dict[UPDATE_TOKEN_NAME]

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
        save_dict = {
            'request': request_object,
            'result': calculation_result
        }
        frequency_save_item = FrequencySaveObject.model_validate(save_dict)
        NicheFrequencyAPI.save(frequency_save_item, self.access_token, self.session_controller, self.request_handler)
        result = NicheFrequencyAPI.get_all(self.access_token, self.session_controller, self.request_handler)

        self.assertEqual(1, len(result))
        saved_object = result[0]
        self.assertEqual(niche_name, saved_object.request.niche)
        self.assertEqual(category_id, saved_object.request.category_id)
        self.assertEqual(marketplace_id, saved_object.request.marketplace_id)

        jorm_result = pydantic_to_jorm(FrequencyResult, calculation_result)
        self.assertEqual(jorm_result.x, saved_object.result.x)
        self.assertEqual(jorm_result.y, saved_object.result.y)

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
        with self.assertRaises(HTTPException):
            NicheFrequencyAPI.calculate(
                request_object,
                self.access_token, self.session_controller
            )

    def test_niche_characteristics_request(self):
        # todo waiting for fix JDB#62
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
        print(calculation_result)

    def test_product_downturn_request(self):
        # todo waiting JDB user's product save
        calculation_result = ProductDownturnAPI.calculate(self.access_token, self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)

    def test_product_turnover_request(self):
        # todo waiting JDB user's product save
        calculation_result = ProductTurnoverAPI.calculate(self.access_token, self.session_controller)
        self.assertIsNotNone(calculation_result)
        print(calculation_result)


if __name__ == '__main__':
    unittest.main()
