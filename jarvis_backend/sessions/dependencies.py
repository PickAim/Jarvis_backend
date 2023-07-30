from fastapi import Depends
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_factory.factories.jcalc import JCalcClassesFactory
from jarvis_factory.factories.jorm import JORMClassesFactory
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.infrastructure import Warehouse, HandlerType, Address
from jorm.market.items import Product
from jorm.market.person import Account, User, UserPrivilege
from passlib.context import CryptContext

from jarvis_backend.auth.hashing.hasher import PasswordHasher
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.db_context import DbContext
from jarvis_backend.sessions.request_handler import RequestHandler, SAVE_METHODS, GET_ALL_METHODS, DELETE_METHODS

__DB_CONTEXT = None
__DEFAULTS_INITED = False


def db_context_depends() -> DbContext:
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


def init_defaults(session):
    __init_admin_account(session)
    marketplace_service = JDBServiceFactory.create_marketplace_service(session)
    default_marketplace = JORMClassesFactory.create_default_marketplace()
    if marketplace_service.find_by_name(default_marketplace.name) is None:
        marketplace_service.create(default_marketplace)
    _, default_marketplace_id = marketplace_service.find_by_name(default_marketplace.name)
    warehouse_service = JDBServiceFactory.create_warehouse_service(session)
    default_warehouse = JORMClassesFactory.create_simple_default_warehouse()
    if warehouse_service.find_warehouse_by_name(default_warehouse.name, default_marketplace_id) is None:
        warehouse_service.create_warehouse(default_warehouse, default_marketplace_id)
    category_service = JDBServiceFactory.create_category_service(session)
    default_category = JORMClassesFactory.create_default_category()
    if category_service.find_by_name(default_category.name, default_marketplace_id) is None:
        category_service.create(default_category, default_marketplace_id)
    niche_service = JDBServiceFactory.create_niche_service(session)
    default_niche = JORMClassesFactory.create_default_niche()
    _, default_category_id = category_service.find_by_name(default_category.name, default_marketplace_id)
    if niche_service.find_by_name(default_niche.name, default_category_id) is None:
        niche_service.create(default_niche, default_category_id)
    _, default_niche_id = niche_service.find_by_name(default_niche.name, default_category_id)
    product_service = JDBServiceFactory.create_product_card_service(session)
    filtered_product_ids = set(
        product_service.filter_existing_global_ids(
            default_niche_id,
            [product.global_id
             for product in default_niche.products]
        )
    )
    if len(filtered_product_ids) > 0:
        __check_warehouse_filled(default_niche.products, warehouse_service, default_marketplace_id)
        _, default_niche_id = niche_service.find_by_name(default_niche.name, default_category_id)
        for product in default_niche.products:
            if product.global_id in filtered_product_ids:
                product_service.create_product(product, default_niche_id)


def __check_warehouse_filled(products: list[Product], warehouse_service: WarehouseService, marketplace_id: int):
    warehouse_ids: set[int] = set()
    for product in products:
        for history_unit in product.history.get_history():
            for warehouse_id in history_unit.leftover:
                warehouse_ids.add(warehouse_id)
    filtered_warehouse_global_ids = warehouse_service.fileter_existing_global_ids(warehouse_ids)
    warehouse_to_add_as_unfilled: list[Warehouse] = []
    for global_id in filtered_warehouse_global_ids:
        warehouse_to_add_as_unfilled.append(__create_warehouse_with_global_id(global_id))
    __fill_warehouses(warehouse_to_add_as_unfilled, warehouse_service, marketplace_id)


def __create_warehouse_with_global_id(global_id: int) -> Warehouse:
    return Warehouse(
        f"unfilled{global_id}",
        global_id,
        HandlerType.MARKETPLACE,
        Address(),
        basic_logistic_to_customer_commission=0,
        additional_logistic_to_customer_commission=0,
        logistic_from_customer_commission=0,
        basic_storage_commission=0,
        additional_storage_commission=0,
        mono_palette_storage_commission=0
    )


def __fill_warehouses(warehouses: list[Warehouse], warehouse_service: WarehouseService, marketplace_id: int):
    for warehouse in warehouses:
        warehouse_service.create_warehouse(warehouse, marketplace_id)


def session_depend(db_context: DbContext = Depends(db_context_depends)):
    global __DEFAULTS_INITED
    with db_context.session() as session, session.begin():
        if not __DEFAULTS_INITED:
            init_defaults(session)
            __DEFAULTS_INITED = True
        yield session


def session_controller_depend(session=Depends(session_depend)) -> JarvisSessionController:
    db_controller = JCalcClassesFactory.create_db_controller(session)
    return JarvisSessionController(db_controller)


def request_handler_depend(session=Depends(session_depend)) -> RequestHandler:
    db_controller = JCalcClassesFactory.create_db_controller(session)
    return RequestHandler(db_controller, SAVE_METHODS, GET_ALL_METHODS, DELETE_METHODS)
