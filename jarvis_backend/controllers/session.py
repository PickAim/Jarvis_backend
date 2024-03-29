import logging
import re
from typing import Callable

import requests
from jarvis_calc.database_interactors.db_controller import DBController
from jarvis_factory.factories.jdb import JDBClassesFactory
from jarvis_factory.factories.jorm import JORMClassesFactory
from jdu.support.constant import WILDBERRIES_NAME
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User, Account
from jorm.server.token.types import TokenType
from jorm.support.calculation import NicheCharacteristicsCalculateResult, GreenTradeZoneCalculateResult
from jorm.support.types import EconomyConstants
from jorm.support.utils import get_request_json
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from jarvis_backend.app.loggers import CONTROLLERS_LOGGER
from jarvis_backend.auth.hashing.hasher import PasswordHasher
from jarvis_backend.auth.tokens.token_control import TokenController
from jarvis_backend.controllers.input import InputController
from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.sessions.request_items import AddApiKeyModel, BasicMarketplaceInfoModel
from jarvis_backend.support.input import InputPreparer

LOGGER = logging.getLogger(CONTROLLERS_LOGGER)


def is_correct_wildberries_api_key(api_key: str) -> bool:
    try:
        headers = {
            'Authorization': api_key
        }
        response = get_request_json("https://suppliers-api.wildberries.ru/api/v3/offices", requests.Session(), headers)
        return len(response) > 0
    except Exception:
        return False


__MARKETPLACE_API_KEY_CORRECTNESS_CHECKS: dict[str, Callable[[str], bool]] = {
    WILDBERRIES_NAME: is_correct_wildberries_api_key
}


def is_correct_marketplace_api_key(api_key: str, marketplace_name: str) -> bool:
    return __MARKETPLACE_API_KEY_CORRECTNESS_CHECKS[marketplace_name](api_key)


class JarvisSessionController:
    def __init__(self, db_controller):
        self.__db_controller: DBController = db_controller
        self.__token_controller = TokenController()
        self.__password_hasher: PasswordHasher = PasswordHasher(
            CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto"))
        self.__jorm_classes_factory: JORMClassesFactory = JORMClassesFactory(self.__db_controller)

    @staticmethod
    def get_cached_niche_characteristics(niche_id: int, session: Session) -> NicheCharacteristicsCalculateResult | None:
        return JDBClassesFactory.create_jorm_collector(session).get_niche_characteristics_cache(niche_id)

    @staticmethod
    def cache_niche_characteristics(niche_id: int,
                                    niche_characteristics: NicheCharacteristicsCalculateResult,
                                    session: Session) -> None:
        changer = JDBClassesFactory.create_jorm_changer(session, 0, 0)
        changer.update_niche_characteristics_cache(niche_id, niche_characteristics)

    @staticmethod
    def get_cached_green_trade_zone_result(niche_id: int, session: Session) -> GreenTradeZoneCalculateResult | None:
        return JDBClassesFactory.create_jorm_collector(session).get_green_zone_cache(niche_id)

    @staticmethod
    def cache_green_trade_zone(niche_id: int,
                               green_trade_zone_result: GreenTradeZoneCalculateResult,
                               session: Session) -> None:
        changer = JDBClassesFactory.create_jorm_changer(session, 0, 0)
        changer.update_green_zone_cache(niche_id, green_trade_zone_result)

    def get_user(self, any_session_token: str) -> User:
        user = self.__db_controller.get_user_by_id(
            self.__token_controller.get_user_id(any_session_token)
        )
        if user is None:
            raise JarvisExceptions.INCORRECT_TOKEN
        return user

    def check_token_correctness(self, token: str, imprint_token: str) -> bool:
        user_id: int = self.__token_controller.get_user_id(token)
        token_type: int = self.__token_controller.get_token_type(token)
        rnd_part: str = self.__token_controller.get_random_part(token)
        try:
            return self.__db_controller.check_token_rnd_part(rnd_part, user_id, imprint_token, token_type)
        except Exception:
            raise JarvisExceptions.INCORRECT_TOKEN

    def update_tokens(self, update_token: str) -> tuple[str, str]:
        user: User = self.get_user(update_token)
        user_id: int = user.user_id
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

    def logout(self, access_token: str, imprint_token: str):
        user_id = self.__token_controller.get_user_id(access_token)
        self.__db_controller.delete_tokens_for_user(user_id, imprint_token)

    def authenticate_user(self, login: str, password: str, imprint_token: str) -> tuple[str, str, str]:
        if "@" not in login:
            login = InputPreparer().prepare_phone_number(login)
        account: Account = self.__db_controller.get_account(login, login)
        if account is not None and self.__password_hasher.verify(password, account.hashed_password):
            user: User = self.__db_controller.get_user_by_account(account)
            return self.__create_tokens_for_user(user.user_id, imprint_token)
        raise JarvisExceptions.INCORRECT_LOGIN_OR_PASSWORD

    def __create_tokens_for_user(self, user_id: int, imprint_token: str) -> tuple[str, str, str]:
        if self.__is_empty_imprint_token(imprint_token):
            return self.__handle_empty_imprint(user_id=user_id)
        return self.__handle_non_empty_imprint(user_id=user_id, imprint_token=imprint_token)

    def __handle_empty_imprint(self, user_id: int) -> tuple[str, str, str]:
        access_token: str = self.__token_controller.create_access_token(user_id)
        access_token_rnd_part: str = self.__token_controller.get_random_part(access_token)
        update_token: str = self.__token_controller.create_update_token(user_id)
        update_token_rnd_part: str = self.__token_controller.get_random_part(update_token)
        imprint_token = self.__token_controller.create_imprint_token()
        self.__db_controller.save_all_tokens(access_token_rnd_part, update_token_rnd_part, imprint_token, user_id)
        return access_token, update_token, imprint_token

    def __handle_non_empty_imprint(self, user_id: int, imprint_token: str) -> tuple[str, str, str]:
        access_token: str = self.__token_controller.create_access_token(user_id)
        access_token_rnd_part: str = self.__token_controller.get_random_part(access_token)
        update_token: str = self.__token_controller.create_update_token(user_id)
        update_token_rnd_part: str = self.__token_controller.get_random_part(update_token)
        is_checked = self.__check_token_exist(user_id=user_id, imprint_token=imprint_token)
        if is_checked:
            self.__db_controller.update_session_tokens_by_imprint(access_token_rnd_part, update_token_rnd_part,
                                                                  imprint_token, user_id)
        else:
            self.__db_controller.save_all_tokens(access_token_rnd_part,
                                                 update_token_rnd_part, imprint_token, user_id)
        return access_token, update_token, imprint_token

    @staticmethod
    def __is_empty_imprint_token(imprint_token: str) -> bool:
        return imprint_token is None or imprint_token == 'None' or imprint_token == 'string'

    def __check_token_exist(self, user_id: int, imprint_token: str) -> bool:
        try:
            return self.__db_controller.check_token_exist(user_id, imprint_token, TokenType.ACCESS.value)
        except Exception:
            return False

    def register_user(self, email: str, password: str, phone_number: str):
        email = InputController.process_email(email)
        phone_number = InputController.process_phone_number(phone_number)
        if (email == "" or email is None) and (phone_number == "" or phone_number is None):
            raise JarvisExceptions.REGISTER_WITHOUT_LOGIN
        account: Account = self.__db_controller.get_account(email, phone_number)
        if account is not None:
            raise JarvisExceptions.EXISTING_LOGIN
        password = InputController.process_password(password)
        hashed_password: str = self.__password_hasher.hash(password)
        account: Account = self.__jorm_classes_factory.create_account(email, hashed_password, phone_number)
        user: User = self.__jorm_classes_factory.create_user()
        self.__db_controller.save_user_and_account(user, account)
        return

    def add_marketplace_api_key(self, add_api_key_request_data: AddApiKeyModel, user_id: int):
        api_key = add_api_key_request_data.api_key
        marketplace_id = add_api_key_request_data.marketplace_id
        id_to_marketplace = self.__db_controller.get_all_marketplaces()
        if marketplace_id not in id_to_marketplace or self.__is_default_object(id_to_marketplace[marketplace_id].name):
            raise JarvisExceptions.INCORRECT_MARKETPLACE
        if not is_correct_marketplace_api_key(api_key, id_to_marketplace[marketplace_id].name):
            raise JarvisExceptions.INCORRECT_MARKETPLACE_API_KEY
        self.__db_controller.add_marketplace_api_key(api_key, user_id, marketplace_id)

    def delete_marketplace_api_key(self, api_key_request_data: BasicMarketplaceInfoModel, user_id: int) -> None:
        self.__db_controller.delete_marketplace_api_key(user_id, api_key_request_data.marketplace_id)

    def delete_account(self, user_id: int) -> None:
        self.__db_controller.delete_account(user_id)

    def get_niche(self, niche_id: int) -> Niche | None:
        result_niche: Niche = self.__db_controller.get_niche_by_id(niche_id)
        return result_niche

    def get_niche_without_history(self, niche_id: int) -> Niche | None:
        result_niche: Niche = self.__db_controller.get_niche_without_history(niche_id)
        return result_niche

    def get_relaxed_niche(self, niche_name: str, category_id: int, marketplace_id: int) -> Niche | None:
        input_preparer = InputPreparer()
        niche_name = input_preparer.prepare_search_string(niche_name)
        result_niche = self.__db_controller.get_niche(niche_name, category_id, marketplace_id)
        if result_niche is not None:
            return result_niche
        default_category_id: int = self.__get_default_category_id(marketplace_id)
        if default_category_id != -1:
            result_niche = self.__db_controller.get_niche(niche_name, category_id, marketplace_id)
            if result_niche is not None:
                LOGGER.debug(f"niche loaded from default category.")
                return result_niche
        result_niche = self.__db_controller.load_new_niche(niche_name, marketplace_id)
        if result_niche is not None:
            LOGGER.debug(f"niche loaded just in time.")
            return result_niche
        return result_niche

    def __get_default_category_id(self, marketplace_id: int) -> int:
        id_to_category = self.__db_controller.get_all_categories(marketplace_id)
        for category_id in id_to_category:
            if self.__is_default_object(id_to_category[category_id].name):
                return category_id
        return -1

    def get_economy_constants(self, marketplace_id: int) -> EconomyConstants:
        return self.__db_controller.get_economy_constants(marketplace_id)

    def get_warehouse(self, warehouse_id: int) -> Warehouse:
        warehouse = self.__db_controller.get_warehouse(warehouse_id)
        if warehouse is not None:
            return warehouse
        return self.__jorm_classes_factory.create_default_warehouse()

    def get_products_by_user(self, user_id: int, marketplace_id: int) -> dict[int, Product]:
        return self.__db_controller.get_products_by_user(user_id, marketplace_id)

    def get_products_by_user_atomic(self, user_id: int, marketplace_id: int) -> dict[int, Product]:
        return self.__db_controller.get_products_by_user_atomic(user_id, marketplace_id)

    @staticmethod
    def __is_default_object(object_name: str) -> bool:
        return re.search('default', object_name, re.IGNORECASE) is not None

    def get_all_marketplaces(self, is_allow_defaults: bool = False) -> dict[int, str]:
        id_to_marketplace = self.__db_controller.get_all_marketplaces()
        result = {}
        for marketplace_id in id_to_marketplace:
            if is_allow_defaults or not self.__is_default_object(id_to_marketplace[marketplace_id].name):
                result[marketplace_id] = id_to_marketplace[marketplace_id].name
        return result

    def get_all_categories(self, marketplace_id: int, is_allow_defaults: bool) -> dict[int, str]:
        id_to_category = self.__db_controller.get_all_categories(marketplace_id)
        result = {}
        for category_id in id_to_category:
            if is_allow_defaults or not self.__is_default_object(id_to_category[category_id].name):
                result[category_id] = id_to_category[category_id].name
        return result

    def get_all_niches(self, category_id: int, is_allow_defaults: bool) -> dict[int, str]:
        id_to_niche = self.__db_controller.get_all_niches(category_id)
        result = {}
        for niche_id in id_to_niche:
            if is_allow_defaults or not self.__is_default_object(id_to_niche[niche_id].name):
                result[niche_id] = id_to_niche[niche_id].name
        return result

    def get_all_warehouses(self, marketplace_id: int, is_allow_defaults: bool) -> dict[int, str]:
        id_to_warehouse = self.__db_controller.get_all_warehouses(marketplace_id)
        result = {}
        for warehouse_id in id_to_warehouse:
            if is_allow_defaults or not self.__is_default_object(id_to_warehouse[warehouse_id].name):
                result[warehouse_id] = id_to_warehouse[warehouse_id].name
        return result
