import json
import unittest

from jarvis_db.db_config import Base
from jarvis_factory.factories.jcalc import JCalcClassesFactory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.exceptions import HTTPException

from app.calc import economy_analyze_requests
from app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from app.session_requests import registrate_user, authenticate_user, auth_by_token, log_out
from app.tokens.dependencies import session_controller_depend
from app.tokens.requests import update_tokens
from sessions.controllers import JarvisSessionController
from sessions.request_items import AuthenticationObject, RegistrationObject, UnitEconomyRequestObject


class DbContext:
    def __init__(self, connection_sting: str = 'sqlite://', echo=False) -> None:
        if echo:
            import logging
            logging.basicConfig()
            logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
        engine = create_engine(connection_sting)
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        self.session = session


class IntegrationTest(unittest.TestCase):
    access_token = ""
    update_token = ""
    imprint_token = ""
    session_controller: JarvisSessionController
    db_context = DbContext(connection_sting='sqlite:///test.db', echo=True)

    def assertAuthentication(self, auth_item, session_controller) -> tuple[str, str, str]:
        response = authenticate_user(auth_item, None, session_controller)
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
        with self.db_context.session() as session, session.begin():
            db_controller = JCalcClassesFactory.create_db_controller(session)
            self.session_controller = session_controller_depend(db_controller)
            # Registration
            try:
                registrate_user(reg_item, self.session_controller)
            except HTTPException:
                pass

            # Authorization by email
            self.assertAuthentication(auth_item_with_email, self.session_controller)
            self.access_token, self.update_token, self.imprint_token = \
                self.assertAuthentication(auth_item_with_phone, self.session_controller)

    def tearDown(self) -> None:
        # Logout
        response = log_out(self.access_token, self.imprint_token, self.session_controller)
        self.assertIsNotNone(response)

    def test_work_with_tokens(self):
        # Auth with token using
        response = auth_by_token(self.access_token, self.imprint_token)
        self.assertTrue(response)

        # Try to update tokens
        response = update_tokens(self.update_token, self.session_controller)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)

        self.access_token = response_dict[ACCESS_TOKEN_NAME]
        self.update_token = response_dict[UPDATE_TOKEN_NAME]

    def test_unit_economy_request(self):
        niche_name: str = "niche"
        buy: int = 50_00
        pack: int = 50_00
        transit_price: int = 1000_00
        transit_count: int = 1000
        marketplace_transit_price: int = 1500_00

        unit_economy_object = {
            "buy": buy,
            "pack": pack,
            "niche": niche_name,
            "transit_count": transit_count,
            "transit_price": transit_price,
            "market_place_transit_price": marketplace_transit_price,
            "warehouse_name": "",
            "marketplace_id": 0
        }
        request = economy_analyze_requests.calculate(
            UnitEconomyRequestObject.parse_obj(unit_economy_object),
            self.access_token, self.session_controller
        )
        self.assertEqual('{"product_cost": 5000, "pack_cost": 5000, "marketplace_commission": 0, "logistic_price": '
                         '200, "storage_price": 0, "margin": -10200, "recommended_price": 0, "transit_profit": '
                         '-10099999, "roi": -1.0099999, "transit_margin": -10099999.0}', request.json())


if __name__ == '__main__':
    unittest.main()
