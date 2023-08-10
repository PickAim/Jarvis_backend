from jarvis_factory.factories.jdu import JDUClassesFactory
from jarvis_factory.support.jdb.services import JDBServiceFactory
from jorm.market.infrastructure import Niche
from jorm.support.constants import DEFAULT_CATEGORY_NAME

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


def __init_tech_no_prom_niche(session):
    marketplace_service = JDBServiceFactory.create_marketplace_service(session)
    found_info = marketplace_service.find_by_name("wildberries")
    _, marketplace_id = found_info
    category_service = JDBServiceFactory.create_category_service(session)
    found_info = category_service.find_by_name(DEFAULT_CATEGORY_NAME, marketplace_id)
    _, category_id = found_info
    niche, niche_id = __fetch_or_load_niche(session, marketplace_id, category_id)
    products = niche.products
    product_card_service = JDBServiceFactory.create_product_card_service(session)
    global_ids = [product.global_id for product in products]
    filtered = set(product_card_service.filter_existing_global_ids(niche_id, global_ids))
    for product in products:
        pass  # TODO find_by_global needed, wait for JDB


def init_tech_no_prom_defaults(session):
    __init_tech_no_prom_niche(session)
