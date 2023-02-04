import re
from dataclasses import dataclass
from functools import lru_cache

from fastapi import HTTPException, status
from jarvis_calc.database_interactors.db_controller import DBController
from jarvis_calc.factories import JORMFactory
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Account, Client

from auth.hashing import PasswordHasher
from auth.tokens.token_control import TokenController
from sessions.exceptions import JarvisExceptionCode
from sessions.request_items import RequestObject


@dataclass
class JarvisSessionController:
    __db_controller: DBController = DBController()
    __tokenizer = TokenController()
    __password_hasher: PasswordHasher = PasswordHasher()
    __jorm_factory: JORMFactory = JORMFactory()

    def get_user(self, access_token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=JarvisExceptionCode.INCORRECT_TOKEN,
        )

        if self.__tokenizer.is_token_expired(access_token):
            raise exception
        user = self.__db_controller.get_user_by_id(
            self.__tokenizer.get_user_id(access_token)
        )
        if user:
            return user
        raise exception

    def update_token(self, update_token: str) -> tuple[str, str]:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=JarvisExceptionCode.INCORRECT_TOKEN
        )

        user_id: int = self.__tokenizer.get_user_id(update_token)
        new_access_token: str = self.__tokenizer.create_access_token(user_id)
        new_update_token: str = self.__tokenizer.create_update_token(user_id)
        try:
            self.__db_controller.update_session_tokens(update_token, new_access_token, new_update_token)
            return new_access_token, new_update_token
        except Exception:
            raise exception

    def authenticate_user(self, login: str, password: str, imprint_token: str) -> tuple[str, str, str]:
        account: Account = self.__db_controller.get_account(login)
        if account is not None and self.__password_hasher.verify(password, account.hashed_password):
            user: User = self.__db_controller.get_user_by_account(account)
            access_token: str = self.__tokenizer.create_access_token(user.user_id)
            update_token: str = self.__tokenizer.create_update_token(user.user_id)
            if imprint_token is not None:
                self.__db_controller.update_session_tokens_by_imprint(access_token, update_token, imprint_token, user)
            else:
                imprint_token: str = self.__tokenizer.create_imprint_token(user.user_id)
                self.__db_controller.save_all_tokens(access_token, update_token, imprint_token, user)
            return access_token, update_token, imprint_token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=JarvisExceptionCode.INCORRECT_LOGIN_OR_PASSWORD,
        )

    def register_user(self, login: str, password: str, phone_number: str):
        account: Account = self.__db_controller.get_account(login)
        if account is None:
            hashed_password: str = self.__password_hasher.hash(password)
            account: Account = self.__jorm_factory.create_account(login, hashed_password, phone_number)
            client: Client = self.__jorm_factory.create_new_client()
            self.__db_controller.save_user_and_account(client, account)
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=JarvisExceptionCode.REGISTER_EXISTING_LOGIN
        )

    @staticmethod
    def __check__password_correctness(password: str) -> int:
        if len(password) <= 8:
            return JarvisExceptionCode.LESS_THAN_8
        if not re.search(r"[a-zа-я]", password):
            return JarvisExceptionCode.NOT_HAS_LOWER_LETTERS
        if not re.search(r"[A-ZА-Я]", password):
            return JarvisExceptionCode.NOT_HAS_UPPER_LETTERS
        if not re.search(r"\d", password):
            return JarvisExceptionCode.NOT_HAS_DIGIT
        if not re.search(r"[_@$]", password):
            return JarvisExceptionCode.NOT_HAS_SPECIAL_SIGNS
        if re.search(r" ", password):
            return JarvisExceptionCode.HAS_WHITE_SPACES
        return 0

    @lru_cache(maxsize=10)
    def get_niche(self, niche_name: str) -> Niche:
        result_niche: Niche = self.__db_controller.get_niche(niche_name)
        if result_niche is None:
            result_niche = self.__db_controller.load_new_niche(niche_name)
        return result_niche

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        return self.__jorm_factory.warehouse(warehouse_name)

    def save_request(self, request_json: str, user: User):
        self.__db_controller.save_request(self.__jorm_factory.request(request_json), user)


class CookieHandler:
    def __init__(self, cookie: any):
        self.access_token, self.update_token, self.imprint_token = self.__extract_tokens_from_cookie(cookie)
        self.is_use_cookie: bool = (self.access_token is not None
                                    and self.update_token is not None
                                    and self.imprint_token is not None)

    def save_to_cookie(self):
        pass

    @staticmethod
    def __extract_tokens_from_cookie(cookie: any) -> tuple[str, str, str]:
        pass


class BaseRequestItemsHandler:
    def __init__(self, base_request_item: RequestObject, cookie: any):
        self.__cookie_controller: CookieHandler = CookieHandler(cookie)
        if self.__cookie_controller.is_use_cookie:
            self.__access_token: str = self.__cookie_controller.access_token
            self.__update_token: str = self.__cookie_controller.update_token
            self.__imprint_token: str = self.__cookie_controller.imprint_token
        else:
            self.__access_token: str = base_request_item.access_token
            self.__update_token: str = base_request_item.update_token
            self.__imprint_token: str = base_request_item.imprint_token

    def get_tokens(self) -> tuple[str, str, str]:
        return self.__access_token, self.__update_token, self.__imprint_token

    def is_use_cookie(self) -> bool:
        return self.__cookie_controller.is_use_cookie

    def save_to_cookie(self) -> None:
        self.__cookie_controller.save_to_cookie()

    def save_token_to_cookie(self, access_token: str, update_token: str, imprint_token: str):
        pass
