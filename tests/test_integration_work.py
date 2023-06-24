import json
import unittest

from jorm.market.service import UnitEconomyResult
from starlette.exceptions import HTTPException

from app.calc.economy_analyze_requests import EconomyAnalyzeAPI
from app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from app.session_requests import SessionAPI
from app.tokens.dependencies import session_controller_depend, request_handler_depend
from app.tokens.requests import TokenAPI
from sessions.controllers import JarvisSessionController, RequestHandler
from sessions.dependencies import _db_context_depends, init_defaults
from sessions.request_items import AuthenticationObject, RegistrationObject, UnitEconomyRequestObject, \
    UnitEconomySaveObject
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
    economy_api = EconomyAnalyzeAPI()

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
            "phone": "+78914561245"
        }
        authentication_by_email_object = {
            "login": "any@mail.com",
            "password": "MyPass1234!",
        }
        authentication_by_phone_object = {
            "login": "+78914561245",
            "password": "MyPass1234!",
        }
        reg_item = RegistrationObject.parse_obj(registration_object)
        auth_item_with_email = AuthenticationObject.parse_obj(authentication_by_email_object)
        auth_item_with_phone = AuthenticationObject.parse_obj(authentication_by_phone_object)
        db_context = _db_context_depends()
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
        niche_name: str = "DEFAULT NICHE"
        category_name: str = "DEFAULT CATEGORY"
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
            "category": category_name,
            "transit_count": transit_count,
            "transit_price": transit_price,
            "market_place_transit_price": marketplace_transit_price,
            "warehouse_name": "",
            "marketplace_id": marketplace_id
        }
        request_object = UnitEconomyRequestObject.parse_obj(unit_economy_object)
        calculation_result = self.economy_api.calculate(
            request_object,
            self.access_token, self.session_controller
        )
        save_dict = {
            'request': request_object,
            'result': calculation_result
        }
        unit_economy_save_item = UnitEconomySaveObject.parse_obj(save_dict)
        self.economy_api.save(unit_economy_save_item, self.access_token, self.session_controller, self.request_handler)
        result = self.economy_api.get_all(self.access_token, self.session_controller, self.request_handler)
        saved_object = result[0]
        self.assertEqual(buy, saved_object.request.buy)
        self.assertEqual(pack, saved_object.request.pack)
        self.assertEqual(niche_name, saved_object.request.niche)
        self.assertEqual(category_name, saved_object.request.category)
        self.assertEqual(transit_count, saved_object.request.transit_count)
        self.assertEqual(transit_price, saved_object.request.transit_price)
        self.assertEqual(marketplace_id, saved_object.request.marketplace_id)

        jorm_result = pydantic_to_jorm(UnitEconomyResult, calculation_result)
        self.assertEqual(jorm_result.product_cost, saved_object.result.product_cost)
        self.assertEqual(jorm_result.pack_cost, saved_object.result.product_cost)
        self.assertEqual(jorm_result.marketplace_commission, saved_object.result.marketplace_commission)
        self.assertEqual(jorm_result.roi, saved_object.result.roi)
        self.assertEqual(jorm_result.logistic_price, saved_object.result.logistic_price)
        self.assertEqual(jorm_result.storage_price, saved_object.result.storage_price)
        self.assertEqual(jorm_result.margin, saved_object.result.margin)
        self.assertEqual(jorm_result.transit_margin, saved_object.result.transit_margin)
        self.assertEqual(jorm_result.recommended_price, saved_object.result.recommended_price)
        self.assertEqual(jorm_result.transit_profit, saved_object.result.transit_profit)


if __name__ == '__main__':
    unittest.main()
