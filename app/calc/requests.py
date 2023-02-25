from fastapi import APIRouter, Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Client

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.handlers import session_controller, calculation_controller
from app.tokens.util import access_token_correctness_depend
from sessions.request_items import UnitEconomyRequestObject

calc_router = APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART)


@calc_router.post('/jorm_margin/')
def calc_margin(unit_economy_item: UnitEconomyRequestObject,
                access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    niche: Niche = session_controller.get_niche(unit_economy_item.niche)
    warehouse: Warehouse = session_controller.get_warehouse(unit_economy_item.warehouse_name)
    result_dict = {}
    if isinstance(user, Client):
        result_dict = calculation_controller.calc_unit_economy(unit_economy_item.buy, unit_economy_item.pack, niche,
                                                               warehouse, user, unit_economy_item.transit_price,
                                                               unit_economy_item.transit_count,
                                                               unit_economy_item.transit_price)
    return result_dict


@calc_router.get('/jorm_data/')
def upload_data(niche_name: str, _: str = Depends(access_token_correctness_depend)):
    niche: Niche = session_controller.get_niche(niche_name)
    x, y = calculation_controller.calc_frequencies(niche)
    return {'x': x, 'y': y}


@calc_router.get('/save_request/')
def save_request_to_history(request_json: str,
                            access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    session_controller.save_request(request_json, user)
