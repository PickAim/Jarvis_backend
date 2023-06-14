from fastapi import Depends
from jarvis_db.repositores.mappers.market.infrastructure import NicheTableToJormMapper, CategoryTableToJormMapper, \
    MarketplaceTableToJormMapper, WarehouseTableToJormMapper
from jarvis_db.repositores.mappers.market.items import ProductTableToJormMapper
from jarvis_db.repositores.market.infrastructure import NicheRepository, CategoryRepository, MarketplaceRepository, \
    WarehouseRepository
from jarvis_db.repositores.market.items import ProductCardRepository
from jarvis_db.services.market.infrastructure.category_service import CategoryService
from jarvis_db.services.market.infrastructure.marketplace_service import MarketplaceService
from jarvis_db.services.market.infrastructure.niche_service import NicheService
from jarvis_db.services.market.infrastructure.warehouse_service import WarehouseService
from jarvis_db.services.market.items.product_card_service import ProductCardService
from jarvis_factory.factories.jorm import JORMClassesFactory

from sessions.db_context import DbContext

__DB_CONTEXT = None
__DEFAULTS_INITED = False


def __db_context_depends() -> DbContext:
    global __DB_CONTEXT
    if __DB_CONTEXT is None:
        __DB_CONTEXT = DbContext("sqlite:///test.db", echo=True)
    return __DB_CONTEXT


def init_defaults(session):
    marketplace_service = MarketplaceService(MarketplaceRepository(session),
                                             MarketplaceTableToJormMapper(WarehouseTableToJormMapper()))
    default_marketplace = JORMClassesFactory.create_default_marketplace()
    if marketplace_service.find_by_name(default_marketplace.name) is None:
        marketplace_service.create(default_marketplace)
    _, default_marketplace_id = marketplace_service.find_by_name(default_marketplace.name)
    warehouse_service = WarehouseService(WarehouseRepository(session), WarehouseTableToJormMapper())
    default_warehouse = JORMClassesFactory.create_simple_default_warehouse()
    if warehouse_service.find_warehouse_by_name(default_warehouse.name) is None:
        warehouse_service.create_warehouse(default_warehouse, default_marketplace_id)
    category_service = CategoryService(CategoryRepository(session),
                                       CategoryTableToJormMapper(NicheTableToJormMapper()))
    default_category = JORMClassesFactory.create_default_category()
    if category_service.find_by_name(default_category.name, default_marketplace_id) is None:
        category_service.create(default_category, default_marketplace_id)
    niche_service = NicheService(NicheRepository(session), NicheTableToJormMapper())
    default_niche = JORMClassesFactory.create_default_niche()
    _, default_category_id = category_service.find_by_name(default_category.name, default_marketplace_id)
    if niche_service.find_by_name(default_niche.name, default_category_id) is None:
        niche_service.create(default_niche, default_category_id)
    product_service = ProductCardService(ProductCardRepository(session), ProductTableToJormMapper())
    filtered_product_ids = product_service.filter_existing_global_ids(
        [product.global_id
         for product in default_niche.products]
    )
    if len(filtered_product_ids) > 0:
        _, default_niche_id = niche_service.find_by_name(default_niche.name, default_category_id)
        for product in default_niche.products:
            product_service.create_product(product, default_niche_id)


def session_depend(db_context: DbContext = Depends(__db_context_depends)):
    global __DEFAULTS_INITED
    with db_context.session() as session, session.begin():
        if not __DEFAULTS_INITED:
            init_defaults(session)
            __DEFAULTS_INITED = True
        yield session
