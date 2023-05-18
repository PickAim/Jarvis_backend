import json
import unittest

from jarvis_db.db_config import Base
from jarvis_factory.factories.jcalc import JCalcClassesFactory
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.exceptions import HTTPException

from app.constants import ACCESS_TOKEN_NAME, UPDATE_TOKEN_NAME, IMPRINT_TOKEN_NAME
from app.session_requests import registrate_user, authenticate_user, auth_by_token, log_out
from app.tokens.dependencies import session_controller_depend
from app.tokens.requests import update_tokens
from sessions.request_items import AuthenticationObject, RegistrationObject


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
    
    def assertAuthentication(self, auth_item, session_controller) -> tuple[str, str, str]:
        response = authenticate_user(auth_item, None, session_controller)
        self.assertIsNotNone(response)
        response_dict = json.loads(response.body.decode())
        self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
        self.assertTrue(UPDATE_TOKEN_NAME in response_dict)
        self.assertTrue(IMPRINT_TOKEN_NAME in response_dict)
        return response_dict[ACCESS_TOKEN_NAME], response_dict[UPDATE_TOKEN_NAME], response_dict[IMPRINT_TOKEN_NAME]

    def test_integration_work(self):
        reg_item = RegistrationObject.parse_obj(self.registration_object)
        auth_item_with_email = AuthenticationObject.parse_obj(self.authentication_by_email_object)
        auth_item_with_phone = AuthenticationObject.parse_obj(self.authentication_by_phone_object)
        db_context = DbContext(connection_sting='sqlite:///test.db', echo=True)
        with db_context.session() as session, session.begin():
            db_controller = JCalcClassesFactory.create_db_controller(session)
            session_controller = session_controller_depend(db_controller)
            # Registration
            try:
                registrate_user(reg_item, session_controller)
            except HTTPException:
                pass

            # Authorization by email
            self.assertAuthentication(auth_item_with_email, session_controller)
            access_token, update_token, imprint_token = \
                self.assertAuthentication(auth_item_with_phone, session_controller)

            # Auth with token using
            response = auth_by_token(access_token, imprint_token)
            self.assertTrue(response)

            # Try to update tokens
            response = update_tokens(update_token, session_controller)
            self.assertIsNotNone(response)
            response_dict = json.loads(response.body.decode())
            self.assertTrue(ACCESS_TOKEN_NAME in response_dict)
            self.assertTrue(UPDATE_TOKEN_NAME in response_dict)

            access_token = response_dict[ACCESS_TOKEN_NAME]
            update_token = response_dict[UPDATE_TOKEN_NAME]

            # Logout
            response = log_out(access_token, imprint_token, session_controller)
            self.assertIsNotNone(response)


if __name__ == '__main__':
    unittest.main()
