from jarvis_db.factories.services import create_user_items_service
from jarvis_factory.factories.jdu import JDUClassesFactory
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.infrastructure import Niche, Category, Marketplace
from jorm.market.items import Product
from jorm.market.person import Account, User, UserPrivilege
from jorm.support.constants import DEFAULT_CATEGORY_NAME
from passlib.context import CryptContext

from jarvis_backend.auth.hashing.hasher import PasswordHasher

__NEEDED_NICHE_NAME = "ножи кухонные набор на подставке"

__PRODUCTS_GLOBAL_IDS_TO_LINK = {146800644, 146423858, 146800701, 28401766, 105341171, 101892545, 161260020}


def __fetch_or_load_niche(session, marketplace_id: int, category_id: int) -> tuple[Niche, int]:
    niche_service = JDBServiceFactory.create_niche_service(session)
    found_info = niche_service.find_by_name(__NEEDED_NICHE_NAME, category_id)
    if found_info is not None:
        _, niche_id = found_info
        niche = niche_service.fetch_by_id_atomic(niche_id)
    else:
        jorm_changer = JDUClassesFactory.create_jorm_changer(session)
        niche = jorm_changer.load_new_niche(__NEEDED_NICHE_NAME, marketplace_id)
        _, niche_id = niche_service.find_by_name(__NEEDED_NICHE_NAME, category_id)
    return niche, niche_id


__DUMMY_USER_EMAIL = "cooluser@jarvis.ru"
__DUMMY_USER_PHONE = ""
__DUMMY_USER_PASSWORD = "IfYouReadThisYouAwesome<666>"


def __init_dummy_user(session) -> int:
    __account_service = JDBServiceFactory.create_account_service(session)
    __user_service = JDBServiceFactory.create_user_service(session)
    found_info: tuple[Account, int] = __account_service.find_by_email_or_phone(__DUMMY_USER_EMAIL, __DUMMY_USER_PHONE)
    if found_info is not None:
        found_info: tuple[User, int] = __user_service.find_by_account_id(found_info[1])
        return found_info[1]

    hashed_password = PasswordHasher(
        CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    ).hash(__DUMMY_USER_PASSWORD)

    user_account = Account(__DUMMY_USER_EMAIL, hashed_password, __DUMMY_USER_PHONE, is_verified_email=True)
    __account_service.create(user_account)
    _, account_id = __account_service.find_by_email(user_account.email)
    user = User(555, name="DUMMY_USER", privilege=UserPrivilege.BASIC)
    __user_service.create(user, account_id)
    found_info: tuple[User, int] = __user_service.find_by_account_id(account_id)
    return found_info[1]


def __init_tech_no_prom_niche(session):
    marketplace_service = JDBServiceFactory.create_marketplace_service(session)
    found_info: tuple[Marketplace, int] = marketplace_service.find_by_name("wildberries")
    _, marketplace_id = found_info
    category_service = JDBServiceFactory.create_category_service(session)
    found_info: tuple[Category, int] = category_service.find_by_name(DEFAULT_CATEGORY_NAME, marketplace_id)
    _, category_id = found_info
    niche, niche_id = __fetch_or_load_niche(session, marketplace_id, category_id)
    products = niche.products
    product_card_service = JDBServiceFactory.create_product_card_service(session)
    global_ids = [product.global_id for product in products]
    filtered = set(product_card_service.filter_existing_global_ids(niche_id, global_ids))
    user_id = __init_dummy_user(session)
    user_items_service = create_user_items_service(session)
    for product in products:
        found_info: tuple[Product, int] = product_card_service.find_by_gloabal_id(product.global_id, marketplace_id)
        user_items_service.append_product(user_id, found_info[1])
        pass  # TODO find_by_global needed, wait for JDB


def init_tech_no_prom_defaults(session):
    __init_tech_no_prom_niche(session)
