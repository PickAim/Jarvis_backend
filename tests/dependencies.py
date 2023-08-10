from jarvis_db.db_config import Base
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_factory.factories.jorm import JORMClassesFactory
from jarvis_factory.startup import init_supported_marketplaces
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.infrastructure import Warehouse, HandlerType, Address
from jorm.market.items import Product
from sqlalchemy import Engine, event, create_engine
from sqlalchemy.orm import sessionmaker

__DEFAULTS_INITED = False
__DB_CONTEXT = None


class TestDbContext:
    def __init__(self, connection_sting: str = 'sqlite://', echo=False) -> None:
        if echo:
            import logging

            logging.basicConfig()
            logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        if connection_sting.startswith("sqlite://"):
            @event.listens_for(Engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

        engine = create_engine(connection_sting)
        session = sessionmaker(bind=engine, autoflush=False)
        Base.metadata.create_all(engine)
        self.session = session


def db_context_depends() -> TestDbContext:
    global __DB_CONTEXT
    if __DB_CONTEXT is None:
        __DB_CONTEXT = TestDbContext("sqlite:///test.db")
    return __DB_CONTEXT


def init_test_defaults(session):
    marketplace_service = JDBServiceFactory.create_marketplace_service(session)
    default_marketplace = JORMClassesFactory.create_default_marketplace()
    if marketplace_service.find_by_name(default_marketplace.name) is None:
        marketplace_service.create(default_marketplace)
    _, default_marketplace_id = marketplace_service.find_by_name(default_marketplace.name)
    init_supported_marketplaces(session)
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


def _get_session(db_context):
    global __DEFAULTS_INITED
    session = db_context.session()
    session.begin()
    if not __DEFAULTS_INITED:
        init_test_defaults(session)
        __DEFAULTS_INITED = True
    return session
