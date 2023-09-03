from fastapi import Depends
from jarvis_factory.factories.jcalc import JCalcClassesFactory
from jarvis_factory.factories.jorm import JORMClassesFactory
from jarvis_factory.startup import init_supported_marketplaces
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.person import Account, User, UserPrivilege
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from jarvis_backend.auth.hashing.hasher import PasswordHasher
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.db_context import DbContext
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.sessions.temp_techno_depends import init_tech_no_prom_defaults

__DB_CONTEXT = None


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


def __init_defaults_for_marketplace(session: Session, marketplace_id: int):
    warehouse_service = JDBServiceFactory.create_warehouse_service(session)
    default_warehouse = JORMClassesFactory.create_simple_default_warehouse()
    if warehouse_service.find_warehouse_by_name(default_warehouse.name, marketplace_id) is None:
        warehouse_service.create_warehouse(default_warehouse, marketplace_id)
    category_service = JDBServiceFactory.create_category_service(session)
    default_category = JORMClassesFactory.create_default_category()
    if category_service.find_by_name(default_category.name, marketplace_id) is None:
        category_service.create(default_category, marketplace_id)


def __init_default_infrastructure(session):
    marketplace_service = JDBServiceFactory.create_marketplace_service(session)
    default_marketplace = JORMClassesFactory.create_default_marketplace()
    if marketplace_service.find_by_name(default_marketplace.name) is None:
        marketplace_service.create(default_marketplace)
    _, default_marketplace_id = marketplace_service.find_by_name(default_marketplace.name)
    __init_defaults_for_marketplace(session, default_marketplace_id)


def init_defaults(session):
    __init_default_infrastructure(session)
    supported_marketplaces_ids = init_supported_marketplaces(session)
    for marketplace_id in supported_marketplaces_ids:
        __init_defaults_for_marketplace(session, marketplace_id)
    init_tech_no_prom_defaults(session)
    __init_admin_account(session)


def session_depend(db_context: DbContext = Depends(db_context_depends)):
    with db_context.session() as session, session.begin():
        yield session


def session_controller_depend(session=Depends(session_depend)) -> JarvisSessionController:
    db_controller = JCalcClassesFactory.create_db_controller(session)
    return JarvisSessionController(db_controller)


def request_handler_depend(session=Depends(session_depend)) -> RequestHandler:
    db_controller = JCalcClassesFactory.create_db_controller(session)
    return RequestHandler(db_controller)
