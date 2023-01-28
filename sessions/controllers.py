import re

from fastapi import HTTPException, status
from jarvis_calc.database_interactors.db_access import DBUpdateProvider, DBAccessProvider
from jarvis_calc.factories import JORMFactory
from jarvis_db.access.accessers import ConcreteDBAccessProvider
from jorm.utils.tokens import Tokenizer
from jorm.utils.hashing import Hasher
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Account, Client

from sessions.exceptions import JarvisException


class JarvisSessionController:
    __tokenizer = Tokenizer()
    __db__accessor: DBAccessProvider = ConcreteDBAccessProvider()
    __db_updater: DBUpdateProvider
    __jorm_factory: JORMFactory = JORMFactory()

    def get_user(self, access_token: str) -> User:
        user = self.__db__accessor.get_user_by_token(Tokenizer.encode_token(access_token))
        if user:
            return user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=JarvisException.INCORRECT_TOKEN,
        )

    def update_token(self, update_token: str) -> tuple[str, str]:
        new_access_token: bytes = self.__tokenizer.create_access_token()
        new_update_token: bytes = self.__tokenizer.create_update_token()
        old_update_token: bytes = Tokenizer.encode_token(update_token)
        try:
            self.__db_updater.update_session_tokens(old_update_token, new_access_token, new_update_token)
            return Tokenizer.decode_token(new_access_token), Tokenizer.decode_token(new_update_token)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=JarvisException.INCORRECT_TOKEN
            )

    def authenticate_user(self, login: str, password: str, imprint_token: bytes) -> tuple[str, str]:
        account: Account = self.__db__accessor.get_account(login)
        if account is not None and Hasher.verify(password, account.hashed_password):
            user: User = self.__db__accessor.get_user(account)
            access_token: bytes = self.__tokenizer.create_access_token()
            update_token: bytes = self.__tokenizer.create_update_token()
            if imprint_token is not None:
                self.__db_updater.update_session_tokens_by_imprint(access_token, update_token, imprint_token, user)
            else:
                imprint_token: bytes = self.__tokenizer.create_imprint_token()
                self.__db_updater.save_all_tokens(access_token, update_token, imprint_token, user)
            return Tokenizer.decode_token(access_token), Tokenizer.decode_token(update_token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=JarvisException.INCORRECT_LOGIN_OR_PASSWORD,
        )

    def register_user(self, login: str, password: str, phone_number: str):
        account: Account = self.__db__accessor.get_account(login)
        if account is None:
            hashed_password: bytes = Hasher.hash(password)
            account: Account = self.__jorm_factory.create_account(login, hashed_password, phone_number)
            client: Client = self.__jorm_factory.create_new_client()
            self.__db_updater.save_user_and_account(client, account)
        raise HTTPException(
            status_code=status.HTTP_208_ALREADY_REPORTED,
            detail=JarvisException.REGISTER_EXISTING_LOGIN
        )

    @staticmethod
    def extract_tokens_from_cookie() -> tuple[bytes, bytes, bytes]:
        pass

    @staticmethod
    def __check__password_correctness(password: str) -> int:
        if len(password) <= 8:
            return JarvisException.LESS_THAN_8
        if not re.search("[a-zа-я]", password):
            return JarvisException.NOT_HAS_LOWER_LETTERS
        if not re.search("[A-ZА-Я]", password):
            return JarvisException.NOT_HAS_UPPER_LETTERS
        if not re.search("\d", password):
            return JarvisException.NOT_HAS_DIGIT
        if not re.search("[_@$]", password):
            return JarvisException.NOT_HAS_SPECIAL_SIGNS
        if re.search(" ", password):
            return JarvisException.HAS_WHITE_SPACES
        return 0

    def niche(self, niche_name: str) -> Niche:
        return self.__jorm_factory.niche(niche_name)

    def warehouse(self, warehouse_name: str) -> Warehouse:
        return self.__jorm_factory.warehouse(warehouse_name)

    def save_request(self, request_json: str, user: User):
        self.__db_updater.save_request(self.__jorm_factory.request(request_json), user)
