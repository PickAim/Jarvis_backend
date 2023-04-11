import re
from dataclasses import dataclass

from fastapi import Cookie
from fastapi.responses import JSONResponse
from jarvis_calc.database_interactors.db_controller import DBController
from jarvis_factory.factories.jcalc import JCalcClassesFactory
from jarvis_factory.factories.jorm import JORMClassesFactory
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Account, Client
from jorm.market.service import UnitEconomyRequest, UnitEconomyResult, FrequencyResult, FrequencyRequest, RequestInfo
from passlib.context import CryptContext
from starlette.responses import Response

from app.constants import ACCESS_TOKEN_USAGE_URL_PART, UPDATE_TOKEN_USAGE_URL_PART
from auth.hashing.hasher import PasswordHasher
from auth.tokens.token_control import TokenController
from sessions.exceptions import JarvisExceptionsCode, JarvisExceptions


@dataclass
class JarvisSessionController:
    __temp_user_count: int = 0
    __db_controller: DBController = JCalcClassesFactory.create_db_controller()
    __tokenizer = TokenController()
    __password_hasher: PasswordHasher = PasswordHasher(CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto"))
    __jorm_classes_factory: JORMClassesFactory = JORMClassesFactory()

    def get_user(self, any_session_token: str) -> User:
        if self.__tokenizer.is_token_expired(any_session_token):
            raise JarvisExceptions.INCORRECT_TOKEN
        user = self.__db_controller.get_user_by_id(
            self.__tokenizer.get_user_id(any_session_token)
        )
        if user:
            return user
        raise JarvisExceptions.INCORRECT_TOKEN

    def check_token_correctness(self, token: str, imprint_token: str) -> bool:
        user_id: int = self.__tokenizer.get_user_id(token)
        token_type: int = self.__tokenizer.get_token_type(token)
        rnd_part: str = self.__tokenizer.get_random_part(token)
        return self.__db_controller.check_token_rnd_part(rnd_part, user_id, imprint_token, token_type)

    def update_tokens(self, update_token: str) -> tuple[str, str]:
        user_id: int = self.__tokenizer.get_user_id(update_token)
        old_update_token_rnd_token: str = self.__tokenizer.get_random_part(update_token)
        new_access_token: str = self.__tokenizer.create_access_token(user_id)
        new_access_token_rnd_part: str = self.__tokenizer.get_random_part(new_access_token)
        new_update_token: str = self.__tokenizer.create_update_token(user_id)
        new_update_token_rnd_part: str = self.__tokenizer.get_random_part(new_update_token)
        try:
            self.__db_controller.update_session_tokens(old_update_token_rnd_token,
                                                       new_access_token_rnd_part, new_update_token_rnd_part)
            return new_access_token, new_update_token
        except Exception:
            raise JarvisExceptions.INCORRECT_TOKEN

    def authenticate_user_by_access_token(self, access_token: str, imprint_token: str) -> tuple[str, str, str]:
        user_id = self.__tokenizer.get_user_id(access_token)
        user: User = self.__db_controller.get_user_by_id(user_id)
        if user is not None:
            return self.__create_tokens_for_user(user, imprint_token)
        raise JarvisExceptions.INCORRECT_TOKEN

    def logout(self, access_token: str, imprint_token: str):
        user_id = self.__tokenizer.get_user_id(access_token)
        self.__db_controller.delete_tokens_for_user(self.__jorm_classes_factory.create_user(user_id), imprint_token)

    def authenticate_user(self, email: str, password: str, phone: str, imprint_token: str) -> tuple[str, str, str]:
        account: Account = self.__db_controller.get_account_by_email(email)
        if account is None:
            account = self.__db_controller.get_account_by_phone(phone)
        if account is not None and self.__password_hasher.verify(password, account.hashed_password):
            user: User = self.__db_controller.get_user_by_account(account)
            return self.__create_tokens_for_user(user, imprint_token)
        raise JarvisExceptions.INCORRECT_LOGIN_OR_PASSWORD

    def __create_tokens_for_user(self, user: User, imprint_token: str) -> tuple[str, str, str]:
        access_token: str = self.__tokenizer.create_access_token(user.user_id)
        access_token_rnd_part: str = self.__tokenizer.get_random_part(access_token)
        update_token: str = self.__tokenizer.create_update_token(user.user_id)
        update_token_rnd_part: str = self.__tokenizer.get_random_part(update_token)
        self.__update_rnd_part_with_imprint(access_token_rnd_part, update_token_rnd_part, imprint_token, user)
        if imprint_token is None or imprint_token == 'None':
            imprint_token = self.__tokenizer.create_imprint_token()
        return access_token, update_token, imprint_token

    def __update_rnd_part_with_imprint(self, access_token_rnd_part: str,
                                       update_token_rnd_part: str, imprint_token: str, user: User):
        if imprint_token is not None:
            try:
                self.__db_controller.update_session_tokens_by_imprint(access_token_rnd_part, update_token_rnd_part,
                                                                      imprint_token, user)
            except Exception:
                raise JarvisExceptions.INCORRECT_TOKEN
        else:
            imprint_token: str = self.__tokenizer.create_imprint_token()
            self.__db_controller.save_all_tokens(access_token_rnd_part, update_token_rnd_part, imprint_token, user)

    def register_user(self, email: str, password: str, phone_number: str):
        account: Account = self.__db_controller.get_account_by_email(email)
        if account is None:
            account = self.__db_controller.get_account_by_phone(phone_number)
        if account is None:
            password_check_status: int = self.__check__password_correctness(password)
            if password_check_status != 0:
                raise JarvisExceptions.create_exception_with_code(password_check_status, "Password check failed")
            hashed_password: str = self.__password_hasher.hash(password)
            account: Account = self.__jorm_classes_factory.create_account(email, hashed_password, phone_number)
            client: Client = self.__jorm_classes_factory.create_new_client()
            client.user_id = self.__temp_user_count
            self.__temp_user_count += 1
            self.__db_controller.save_user_and_account(client, account)
            return
        raise JarvisExceptions.EXISTING_LOGIN

    @staticmethod
    def __check__password_correctness(password: str) -> int:
        if len(password) < 8:
            return JarvisExceptionsCode.LESS_THAN_8
        if not re.search(r"[a-zа-я]", password):
            return JarvisExceptionsCode.NOT_HAS_LOWER_LETTERS
        if not re.search(r"[A-ZА-Я]", password):
            return JarvisExceptionsCode.NOT_HAS_UPPER_LETTERS
        if not re.search(r"\d", password):
            return JarvisExceptionsCode.NOT_HAS_DIGIT
        if not re.search(r"[!@#$%^&*()_+~]", password):
            return JarvisExceptionsCode.NOT_HAS_SPECIAL_SIGNS
        if re.search(r" ", password):
            return JarvisExceptionsCode.HAS_WHITE_SPACES
        return 0

    def get_niche(self, niche_name: str) -> Niche:
        result_niche: Niche = self.__db_controller.get_niche(niche_name)
        if result_niche is None:
            result_niche = self.__db_controller.load_new_niche(niche_name)
        return result_niche

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        return self.__jorm_classes_factory.warehouse(warehouse_name)


class RequestHandler:
    __db_controller: DBController = JCalcClassesFactory.create_db_controller()

    def save_unit_economy_request(self, request: UnitEconomyRequest, result: UnitEconomyResult,
                                  info: RequestInfo, user: User) -> int:
        return self.__db_controller.save_unit_economy_request(request, result, info, user)

    def save_frequency_request(self, request: FrequencyRequest, result: FrequencyResult,
                               info: RequestInfo, user: User) -> int:
        return self.__db_controller.save_frequency_request(request, result, info, user)

    def get_all_unit_economy_results(self, user: User) \
            -> list[tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
        return self.__db_controller.get_all_unit_economy_results(user)


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
