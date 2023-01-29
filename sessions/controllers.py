import re
from dataclasses import dataclass

from fastapi import HTTPException, status
from jarvis_calc.database_interactors.db_access import DBUpdateProvider, DBAccessProvider
from jarvis_calc.factories import JORMFactory
from jarvis_db.access.accessers import ConcreteDBAccessProvider
from jorm.utils.tokens import Tokenizer
from jorm.utils.hashing import Hasher
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Account, Client

from sessions.exceptions import JarvisExceptionCode


@dataclass
class JarvisSessionController:
    __db_updater: DBUpdateProvider
    __tokenizer = Tokenizer()
    __hasher: Hasher = Hasher()
    __db__accessor: DBAccessProvider = ConcreteDBAccessProvider()
    __jorm_factory: JORMFactory = JORMFactory()

    def get_user(self, access_token: str) -> User:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=JarvisExceptionCode.INCORRECT_TOKEN,
        )
        if self.__tokenizer.is_token_expired(access_token):
            raise exception
        user = self.__db__accessor.get_user_by_id(
            self.__tokenizer.extract_encoded_data(access_token)[self.__tokenizer.USER_ID_KEY]
        )
        if user:
            return user
        raise exception

    def update_token(self, update_token: str) -> tuple[str, str]:
        user_id: int = self.__tokenizer.extract_encoded_data(update_token)[self.__tokenizer.USER_ID_KEY]
        new_access_token: str = self.__tokenizer.create_access_token(user_id)
        new_update_token: str = self.__tokenizer.create_update_token(user_id)
        try:
            self.__db_updater.update_session_tokens(update_token, new_access_token, new_update_token)
            return new_access_token, new_update_token
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=JarvisExceptionCode.INCORRECT_TOKEN
            )

    def authenticate_user(self, login: str, password: str, imprint_token: str) -> tuple[str, str]:
        account: Account = self.__db__accessor.get_account(login)
        if account is not None and self.__hasher.verify(password, account.hashed_password):
            user: User = self.__db__accessor.get_user_by_account(account)
            access_token: str = self.__tokenizer.create_access_token(user.user_id)
            update_token: str = self.__tokenizer.create_update_token(user.user_id)
            if imprint_token is not None:
                self.__db_updater.update_session_tokens_by_imprint(access_token, update_token, imprint_token, user)
            else:
                imprint_token: str = self.__tokenizer.create_imprint_token(user.user_id)
                self.__db_updater.save_all_tokens(access_token, update_token, imprint_token, user)
            return access_token, update_token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=JarvisExceptionCode.INCORRECT_LOGIN_OR_PASSWORD,
        )

    def register_user(self, login: str, password: str, phone_number: str):
        account: Account = self.__db__accessor.get_account(login)
        if account is None:
            hashed_password: str = self.__hasher.hash(password)
            account: Account = self.__jorm_factory.create_account(login, hashed_password, phone_number)
            client: Client = self.__jorm_factory.create_new_client()
            self.__db_updater.save_user_and_account(client, account)
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=JarvisExceptionCode.REGISTER_EXISTING_LOGIN
        )

    @staticmethod
    def extract_tokens_from_cookie() -> tuple[bytes, bytes, bytes]:
        pass

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

    def get_niche(self, niche_name: str) -> Niche:
        return self.__jorm_factory.niche(niche_name)

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        return self.__jorm_factory.warehouse(warehouse_name)

    def save_request(self, request_json: str, user: User):
        self.__db_updater.save_request(self.__jorm_factory.request(request_json), user)
