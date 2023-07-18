import logging

from fastapi import Cookie
from jarvis_calc.database_interactors.db_controller import DBController
from jarvis_factory.factories.jorm import JORMClassesFactory
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User, Account
from jorm.support.constants import DEFAULT_CATEGORY_NAME
from passlib.context import CryptContext
from starlette.responses import JSONResponse, Response

from app.constants import ACCESS_TOKEN_USAGE_URL_PART, UPDATE_TOKEN_USAGE_URL_PART
from app.loggers import CONTROLLERS_LOGGER
from auth.hashing.hasher import PasswordHasher
from auth.tokens.token_control import TokenController
from sessions.exceptions import JarvisExceptions
from support.input import InputValidator, InputPreparer

LOGGER = logging.getLogger(CONTROLLERS_LOGGER)


class InputController:
    @staticmethod
    def process_phone_number(phone_number: str) -> str:
        input_preparer = InputPreparer()
        input_validator = InputValidator()
        phone_number = input_preparer.prepare_phone_number(phone_number)
        phone_check_status = input_validator.check_phone_number_correctness(phone_number)
        if phone_check_status != 0:
            raise JarvisExceptions.create_exception_with_code(phone_check_status, "Phone number check failed")
        return phone_number

    @staticmethod
    def process_password(password: str) -> str:
        input_validator = InputValidator()
        password_check_status: int = input_validator.check_password_correctness(password)
        if password_check_status != 0:
            raise JarvisExceptions.create_exception_with_code(password_check_status, "Password check failed")
        return password


class JarvisSessionController:
    def __init__(self, db_controller):
        self.temp_user_count: int = 0
        self.__db_controller: DBController = db_controller
        self.__token_controller = TokenController()
        self.__password_hasher: PasswordHasher = PasswordHasher(
            CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto"))
        self.__jorm_classes_factory: JORMClassesFactory = JORMClassesFactory(self.__db_controller)

    def get_user(self, any_session_token: str) -> User:
        user = self.__db_controller.get_user_by_id(
            self.__token_controller.get_user_id(any_session_token)
        )
        if user:
            return user
        raise JarvisExceptions.INCORRECT_TOKEN

    def check_token_correctness(self, token: str, imprint_token: str) -> bool:
        user_id: int = self.__token_controller.get_user_id(token)
        token_type: int = self.__token_controller.get_token_type(token)
        rnd_part: str = self.__token_controller.get_random_part(token)
        return self.__db_controller.check_token_rnd_part(rnd_part, user_id, imprint_token, token_type)

    def update_tokens(self, update_token: str) -> tuple[str, str]:
        user_id: int = self.__token_controller.get_user_id(update_token)
        old_update_token_rnd_token: str = self.__token_controller.get_random_part(update_token)
        new_access_token: str = self.__token_controller.create_access_token(user_id)
        new_access_token_rnd_part: str = self.__token_controller.get_random_part(new_access_token)
        new_update_token: str = self.__token_controller.create_update_token(user_id)
        new_update_token_rnd_part: str = self.__token_controller.get_random_part(new_update_token)
        try:
            self.__db_controller.update_session_tokens(user_id, old_update_token_rnd_token,
                                                       new_access_token_rnd_part, new_update_token_rnd_part)
            return new_access_token, new_update_token
        except Exception:
            raise JarvisExceptions.INCORRECT_TOKEN

    def authenticate_user_by_access_token(self, access_token: str, imprint_token: str) -> tuple[str, str, str]:
        user_id = self.__token_controller.get_user_id(access_token)
        user: User = self.__db_controller.get_user_by_id(user_id)
        if user is not None:
            return self.__create_tokens_for_user(user.user_id, imprint_token)
        raise JarvisExceptions.INCORRECT_TOKEN

    def logout(self, access_token: str, imprint_token: str):
        user_id = self.__token_controller.get_user_id(access_token)
        self.__db_controller.delete_tokens_for_user(user_id, imprint_token)

    def authenticate_user(self, login: str, password: str, imprint_token: str) -> tuple[str, str, str]:
        account: Account = self.__db_controller.get_account(login, login)
        if account is not None and self.__password_hasher.verify(password, account.hashed_password):
            user: User = self.__db_controller.get_user_by_account(account)
            return self.__create_tokens_for_user(user.user_id, imprint_token)
        raise JarvisExceptions.INCORRECT_LOGIN_OR_PASSWORD

    def __create_tokens_for_user(self, user_id: int, imprint_token: str) -> tuple[str, str, str]:
        access_token: str = self.__token_controller.create_access_token(user_id)
        access_token_rnd_part: str = self.__token_controller.get_random_part(access_token)
        update_token: str = self.__token_controller.create_update_token(user_id)
        update_token_rnd_part: str = self.__token_controller.get_random_part(update_token)
        if imprint_token is not None and imprint_token != 'None':
            try:
                self.__db_controller.update_session_tokens_by_imprint(access_token_rnd_part, update_token_rnd_part,
                                                                      imprint_token, user_id)
                return access_token, update_token, imprint_token
            except Exception:
                imprint_token = self.__token_controller.create_imprint_token()
        else:
            imprint_token = self.__token_controller.create_imprint_token()
        self.__db_controller.save_all_tokens(access_token_rnd_part, update_token_rnd_part, imprint_token, user_id)
        return access_token, update_token, imprint_token

    def register_user(self, email: str, password: str, phone_number: str):
        if email == '':
            email = None
        if phone_number == '':
            phone_number = None
        account: Account = self.__db_controller.get_account(email, phone_number)
        if account is not None:
            raise JarvisExceptions.EXISTING_LOGIN
        password = InputController.process_password(password)
        phone_number = InputController.process_phone_number(phone_number)
        hashed_password: str = self.__password_hasher.hash(password)
        account: Account = self.__jorm_classes_factory.create_account(email, hashed_password, phone_number)
        user: User = self.__jorm_classes_factory.create_user(self.temp_user_count)
        user.user_id = self.temp_user_count
        self.temp_user_count += 1  # TODO remove it after real JDB implementation
        self.__db_controller.save_user_and_account(user, account)
        return

    def get_niche(self, niche_name: str, category_id: int, marketplace_id: int) -> Niche | None:
        input_preparer = InputPreparer()
        niche_name = input_preparer.prepare_search_string(niche_name)
        result_niche: Niche = self.__db_controller.get_niche(niche_name, category_id, marketplace_id)
        return result_niche

    def get_relaxed_niche(self, niche_name: str, category_id: int, marketplace_id: int) -> Niche:
        input_preparer = InputPreparer()
        niche_name = input_preparer.prepare_search_string(niche_name)
        result_niche = self.get_niche(niche_name, category_id, marketplace_id)
        if result_niche is not None:
            return result_niche
        result_niche = self.__db_controller.get_niche(niche_name, DEFAULT_CATEGORY_NAME, marketplace_id)
        if result_niche is not None:
            LOGGER.debug(f"niche loaded from default category.")
            return result_niche
        result_niche = self.__db_controller.load_new_niche(niche_name)
        if result_niche is not None:
            LOGGER.debug(f"niche loaded just in time.")
            return result_niche
        LOGGER.debug(f"default niche created.")
        return self.__jorm_classes_factory.create_default_niche()

    def get_warehouse(self, warehouse_name: str, marketplace_id: int) -> Warehouse:
        warehouse = self.__db_controller.get_warehouse(warehouse_name, marketplace_id)
        if warehouse is not None:
            return warehouse
        reference_warehouses = self.__db_controller.get_all_warehouses(marketplace_id)
        return self.__jorm_classes_factory.create_default_warehouse(reference_warehouses)

    def get_products_by_user(self, user_id: int) -> list[Product]:
        return self.__db_controller.get_products_by_user(user_id)

    def get_all_marketplaces(self) -> dict[int, str]:
        id_to_marketplace = self.__db_controller.get_all_marketplaces()
        return {
            marketplace_id: id_to_marketplace[marketplace_id].name
            for marketplace_id in id_to_marketplace
        }

    def get_all_categories(self, marketplace_id: int) -> dict[int, str]:
        id_to_category = self.__db_controller.get_all_categories(marketplace_id)
        return {
            category_id: id_to_category[category_id].name
            for category_id in id_to_category
        }

    def get_all_niches(self, category_id: int, marketplace_id: int) -> dict[int, str]:
        id_to_niche = self.__db_controller.get_all_niches(category_id, marketplace_id)
        return {
            niche_id: id_to_niche[niche_id].name
            for niche_id in id_to_niche
        }


class CookieHandler:
    @staticmethod
    def save_access_token(response: Response, access_token: str) -> Response:
        response.set_cookie(key="cookie_access_token", path=ACCESS_TOKEN_USAGE_URL_PART,
                            value=access_token, httponly=True, secure=True)
        return response

    @staticmethod
    def save_update_token(response: Response, update_token: str) -> Response:
        response.set_cookie(key="cookie_update_token", value=update_token, httponly=True,
                            secure=True)
        return response

    @staticmethod
    def save_imprint_token(response: Response, imprint_token: str) -> Response:
        response.set_cookie(key="cookie_imprint_token", value=imprint_token, httponly=True, secure=True)
        return response

    @staticmethod
    def load_access_token(cookie_access_token: str = Cookie(default=None)) -> str | None:
        return cookie_access_token

    @staticmethod
    def load_update_token(cookie_update_token: str = Cookie(default=None)) -> str | None:
        return cookie_update_token

    @staticmethod
    def load_imprint_token(cookie_imprint_token: str = Cookie(default=None)) -> str | None:
        return cookie_imprint_token

    @staticmethod
    def delete_all_cookie(response: JSONResponse) -> JSONResponse:
        response.delete_cookie("cookie_access_token", path=ACCESS_TOKEN_USAGE_URL_PART, httponly=True, secure=True)
        response.delete_cookie("cookie_update_token", path=UPDATE_TOKEN_USAGE_URL_PART, httponly=True, secure=True)
        return response
