import re
from dataclasses import dataclass
from functools import lru_cache

from fastapi import Cookie
from fastapi.responses import JSONResponse
from jarvis_calc.database_interactors.db_controller import DBController
from jarvis_calc.factories import JORMFactory
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Account, Client
from starlette.responses import Response

from auth.hashing import PasswordHasher
from auth.tokens.token_control import TokenController
from sessions.exceptions import JarvisExceptionsCode, JarvisExceptions


@dataclass
class JarvisSessionController:
    __db_controller: DBController = DBController()
    __tokenizer = TokenController()
    __password_hasher: PasswordHasher = PasswordHasher()
    __jorm_factory: JORMFactory = JORMFactory()

    def get_user(self, any_session_token: str) -> User:
        if self.__tokenizer.is_token_expired(any_session_token):
            raise JarvisExceptions.INCORRECT_TOKEN
        user = self.__db_controller.get_user_by_id(
            self.__tokenizer.get_user_id(any_session_token)
        )
        if user:
            return user
        raise JarvisExceptions.INCORRECT_TOKEN

    def update_token(self, update_token: str) -> tuple[str, str]:
        return "newa", "newu"
        # exception = HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail=JarvisExceptionCode.INCORRECT_TOKEN
        # )
        #
        # user_id: int = self.__tokenizer.get_user_id(update_token)
        # new_access_token: str = self.__tokenizer.create_access_token(user_id)
        # new_update_token: str = self.__tokenizer.create_update_token(user_id)
        # try:
        #     self.__db_controller.update_session_tokens(update_token, new_access_token, new_update_token)
        #     return new_access_token, new_update_token
        # except Exception:
        #     raise exception

    def authenticate_user(self, login: str, password: str, imprint_token: str) -> tuple[str, str, str]:
        account: Account = self.__db_controller.get_account(login)
        if account is not None and self.__password_hasher.verify(password, account.hashed_password):
            user: User = self.__db_controller.get_user_by_account(account)
            access_token: str = self.__tokenizer.create_access_token(user.user_id)
            update_token: str = self.__tokenizer.create_update_token(user.user_id)
            if imprint_token is not None:
                try:
                    self.__db_controller.update_session_tokens_by_imprint(access_token, update_token, imprint_token,
                                                                          user)
                except Exception:
                    raise JarvisExceptions.INCORRECT_TOKEN
            else:
                imprint_token: str = self.__tokenizer.create_imprint_token(user.user_id)
                self.__db_controller.save_all_tokens(access_token, update_token, imprint_token, user)
            return access_token, update_token, imprint_token
        raise JarvisExceptions.INCORRECT_LOGIN_OR_PASSWORD

    def register_user(self, login: str, password: str, phone_number: str):
        account: Account = self.__db_controller.get_account(login)
        if account is None:
            hashed_password: str = self.__password_hasher.hash(password)
            account: Account = self.__jorm_factory.create_account(login, hashed_password, phone_number)
            client: Client = self.__jorm_factory.create_new_client()
            self.__db_controller.save_user_and_account(client, account)
        raise JarvisExceptions.EXISTING_LOGIN

    @staticmethod
    def __check__password_correctness(password: str) -> int:
        if len(password) <= 8:
            return JarvisExceptionsCode.LESS_THAN_8
        if not re.search(r"[a-zа-я]", password):
            return JarvisExceptionsCode.NOT_HAS_LOWER_LETTERS
        if not re.search(r"[A-ZА-Я]", password):
            return JarvisExceptionsCode.NOT_HAS_UPPER_LETTERS
        if not re.search(r"\d", password):
            return JarvisExceptionsCode.NOT_HAS_DIGIT
        if not re.search(r"[_@$]", password):
            return JarvisExceptionsCode.NOT_HAS_SPECIAL_SIGNS
        if re.search(r" ", password):
            return JarvisExceptionsCode.HAS_WHITE_SPACES
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

    @staticmethod
    def save_access_token(response: Response, access_token: str) -> Response:
        response.set_cookie(key="access_token", value=access_token, path="/any", httponly=True, secure=True)
        return response

    @staticmethod
    def save_update_token(response: Response, update_token: str) -> Response:
        response.set_cookie(key="update_token", value=update_token, path="/items", httponly=True, secure=True)
        return response

    @staticmethod
    def save_imprint_token(response: Response, imprint_token: str) -> Response:
        response.set_cookie(key="imprint_token", value=imprint_token, path="/any", httponly=True, secure=True)
        return response

    @staticmethod
    def load_access_token(access_token: str = Cookie(default=None)) -> str | None:
        return access_token

    @staticmethod
    def load_update_token(update_token: str = Cookie(default=None)) -> str | None:
        return update_token

    @staticmethod
    def load_imprint_token(imprint_token: str = Cookie(default=None)) -> str | None:
        return imprint_token

    @staticmethod
    def delete_all_cookie(response: JSONResponse) -> JSONResponse:
        response.delete_cookie("access_token")
        response.delete_cookie("update_token")
        response.delete_cookie("imprint_token")
        return response

#
# class BaseRequestItemsHandler:
#     def __init__(self, base_request_item: RequestObject, token_model: TokenModel):
#         self.is_use_cookie = True
#         if base_request_item.is_token_init():
#             self.is_use_cookie = False
#             access_token: str = base_request_item.access_token
#             update_token: str = base_request_item.update_token
#             imprint_token: str = base_request_item.imprint_token
#         else:
#             if token_model is None or token_model.is_empty():
#                 raise JarvisExceptions.INCORRECT_TOKEN
#             access_token: str = base_request_item.access_token
#             update_token: str = base_request_item.update_token
#             imprint_token: str = base_request_item.imprint_token
#         self.__token_model: TokenModel = TokenModel(access_token, update_token, imprint_token)
#
#     def get_token_model(self) -> TokenModel:
#         return self.__token_model
#
#     def set_token_model(self, token_model: TokenModel) -> None:
#         self.__token_model = token_model
#
#     def save_to_cookie(self, response: JSONResponse) -> JSONResponse:
#         return CookieHandler.save_token_to_cookie(response, self.__token_model)
