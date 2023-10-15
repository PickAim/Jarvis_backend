from fastapi import Depends
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_factory.factories.jcalc import JCalcClassesFactory
from jarvis_factory.factories.jorm import JORMClassesFactory
from jarvis_factory.startup import init_supported_marketplaces
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.infrastructure import Warehouse, HandlerType, Address
from jorm.market.items import Product
from jorm.market.person import Account, User, UserPrivilege
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from jarvis_backend.app.config.launch import LaunchConfigHolder
from jarvis_backend.app.constants import LAUNCH_CONFIGS
from jarvis_backend.auth.hashing.hasher import PasswordHasher
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.db_context import DbContext
from jarvis_backend.sessions.request_handler import RequestHandler

__DB_CONTEXT = None


def db_context_depend() -> DbContext:
    global __DB_CONTEXT
    if __DB_CONTEXT is None:
        __DB_CONTEXT = DbContext("sqlite:///test.db")
    return __DB_CONTEXT


def __init_admin_account(session):
    __account_service = JDBServiceFactory.create_account_service(session)
    admin_email = "admin@mail.com"
    admin_phone = "+11111111111"
    if __account_service.find_by_email_or_phone(admin_email, admin_phone) is not None:
        return
    admin_password = "Apassword123!"
    hashed_password = PasswordHasher(CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")).hash(admin_password)
    admin_account = Account(admin_email, hashed_password, admin_phone, is_verified_email=True)
    __account_service.create(admin_account)
    _, account_id = __account_service.find_by_email(admin_account.email)
    admin_user = User(1, name="ADMIN", privilege=UserPrivilege.DUNGEON_MASTER)
    __user_service = JDBServiceFactory.create_user_service(session)
    __user_service.create(admin_user, account_id)


def __init_defaults_for_marketplace(session: Session, marketplace_id: int):
    warehouse_service = JDBServiceFactory.create_warehouse_service(session)
    default_warehouse = JORMClassesFactory.create_default_warehouse()
    if warehouse_service.find_warehouse_by_name(default_warehouse.name, marketplace_id) is None:
        warehouse_service.create_warehouse(default_warehouse, marketplace_id)
    category_service = JDBServiceFactory.create_category_service(session)
    default_category = JORMClassesFactory.create_default_category()
    if category_service.find_by_name(default_category.name, marketplace_id) is None:
        category_service.create(default_category, marketplace_id)

    _, category_id = category_service.find_by_name(default_category.name, marketplace_id)
    niche_service = JDBServiceFactory.create_niche_service(session)
    default_niche = JORMClassesFactory.create_default_niche()
    if niche_service.find_by_name(default_niche.name, category_id) is None:
        niche_service.create(default_niche, category_id)
    _, default_niche_id = niche_service.find_by_name(default_niche.name, category_id)
    product_service = JDBServiceFactory.create_product_card_service(session)
    filtered_product_ids = set(
        product_service.filter_existing_global_ids(
            default_niche_id,
            [product.global_id
             for product in default_niche.products]
        )
    )
    if len(filtered_product_ids) > 0:
        __check_warehouse_filled(default_niche.products, warehouse_service, marketplace_id)
        _, default_niche_id = niche_service.find_by_name(default_niche.name, category_id)
        for product in default_niche.products:
            if product.global_id in filtered_product_ids:
                product_service.create_product(product, default_niche_id)


def __check_warehouse_filled(products: list[Product], warehouse_service: WarehouseService, marketplace_id: int):
    warehouse_ids: set[int] = set()
    for product in products:
        for history_unit in product.history.get_history():
            for warehouse_id in history_unit.leftover:
                warehouse_ids.add(warehouse_id)
    filtered_warehouse_global_ids = warehouse_service.filter_existing_global_ids(warehouse_ids)
    warehouse_to_add_as_unfilled: list[Warehouse] = []
    for global_id in filtered_warehouse_global_ids:
        warehouse_to_add_as_unfilled.append(__create_warehouse_with_global_id(global_id))
    __fill_warehouses(warehouse_to_add_as_unfilled, warehouse_service, marketplace_id)


def __create_warehouse_with_global_id(global_id: int) -> Warehouse:
    return Warehouse(
        f"unfilled{global_id}",
        global_id,
        HandlerType.MARKETPLACE,
        Address()
    )


def __fill_warehouses(warehouses: list[Warehouse], warehouse_service: WarehouseService, marketplace_id: int):
    for warehouse in warehouses:
        warehouse_service.create_warehouse(warehouse, marketplace_id)


__DUMMY_USER_EMAIL = "dummy"
__DUMMY_USER_PHONE = ""
__DUMMY_USER_PASSWORD = "dummy"


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


def __init_product_for_dummy_user(session: Session, user_id: int):
    user_items_service = JDBServiceFactory.create_user_items_service(session)
    id_to_product = user_items_service.fetch_user_products(user_id, marketplace_id=2)  # hardcoded second mp
    if len(id_to_product) != 0:
        return
    for product_id in range(605, 615):
        user_items_service.append_product(user_id, product_id)


def __init_default_infrastructure(session):
    marketplace_service = JDBServiceFactory.create_marketplace_service(session)
    default_marketplace = JORMClassesFactory.create_default_marketplace()
    if marketplace_service.find_by_name(default_marketplace.name) is None:
        marketplace_service.create(default_marketplace)
    _, default_marketplace_id = marketplace_service.find_by_name(default_marketplace.name)
    __init_defaults_for_marketplace(session, default_marketplace_id)
    supported_marketplaces_ids = init_supported_marketplaces(session)
    for marketplace_id in supported_marketplaces_ids:
        __init_defaults_for_marketplace(session, marketplace_id)
    dummy_user_id: int = __init_dummy_user(session)
    __init_product_for_dummy_user(session, dummy_user_id)


def __delete_defaults(session):
    # marketplace_service = JDBServiceFactory.create_marketplace_service(session)
    # default_marketplace = JORMClassesFactory.create_default_marketplace()
    # found = marketplace_service.find_by_name(default_marketplace.name)
    # if found is not None:
    #     _, marketplace_id = found
    #     marketplace_service.

    account_service = JDBServiceFactory.create_account_service(session)
    found = account_service.find_by_email_or_phone(__DUMMY_USER_EMAIL, __DUMMY_USER_PHONE)
    if found is None:
        return
    _, account_id = found
    user_service = JDBServiceFactory.create_user_service(session)
    found = user_service.find_by_account_id(account_id)
    if found is None:
        return
    _, user_id = found
    user_service.delete(user_id)


def init_defaults(session):
    config_holder = LaunchConfigHolder(LAUNCH_CONFIGS)
    if config_holder.dummies_enabled:
        __init_default_infrastructure(session)
    else:
        __delete_defaults(session)
        init_supported_marketplaces(session)
    __init_admin_account(session)


def session_depend(db_context: DbContext = Depends(db_context_depend)):
    with db_context.session() as session, session.begin():
        yield session


def session_controller_depend(session: Session, marketplace_id: int = 0, user_id: int = 0) -> JarvisSessionController:
    db_controller = JCalcClassesFactory.create_db_controller(session=session,
                                                             marketplace_id=marketplace_id,
                                                             user_id=user_id)
    return JarvisSessionController(db_controller)


def request_handler_depend(session: Session,
                           marketplace_id: int = 0,
                           user_id: int = 0) -> RequestHandler:
    db_controller = JCalcClassesFactory.create_db_controller(session=session,
                                                             marketplace_id=marketplace_id,
                                                             user_id=user_id)
    return RequestHandler(db_controller)
