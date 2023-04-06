from fastapi import APIRouter, Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Client

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.handlers import session_controller, calculation_controller
from app.tokens.dependencies import access_token_correctness_depend
from sessions.request_items import UnitEconomyRequestObject, UnitEconomyResultObject, UnitEconomySaveObject

UNIT_ECON_URL_PART = "/unit_econ"

unit_economy_router = APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART)


@unit_economy_router.post(UNIT_ECON_URL_PART + '/calculate/')
def calculate(unit_economy_item: UnitEconomyRequestObject,
              access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    niche: Niche = session_controller.get_niche(unit_economy_item.niche)
    warehouse: Warehouse = session_controller.get_warehouse(unit_economy_item.warehouse_name)
    result: UnitEconomyResultObject | None = None
    if isinstance(user, Client):
        result = calculation_controller.calc_unit_economy(unit_economy_item.buy, unit_economy_item.pack, niche,
                                                          warehouse, user, unit_economy_item.transit_price,
                                                          unit_economy_item.transit_count,
                                                          unit_economy_item.transit_price)
    return result


@unit_economy_router.post(UNIT_ECON_URL_PART + '/save/')
def save(unit_economy_save_item: UnitEconomySaveObject,
         access_token: str = Depends(access_token_correctness_depend)):
    pass


@unit_economy_router.post(UNIT_ECON_URL_PART + '/get-all/')
def get_all(access_token: str = Depends(access_token_correctness_depend)):
    pass
