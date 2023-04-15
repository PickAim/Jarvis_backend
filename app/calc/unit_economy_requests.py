from datetime import datetime

from fastapi import APIRouter, Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Client
from jorm.market.service import UnitEconomyRequest, RequestInfo as JRequestInfo, UnitEconomyResult

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.handlers import session_controller, calculation_controller, request_handler
from app.tokens.dependencies import access_token_correctness_depend
from sessions.request_items import UnitEconomyRequestObject, UnitEconomyResultObject, UnitEconomySaveObject, RequestInfo
from support.utils import pydantic_to_jorm, jorm_to_pydantic

UNIT_ECON_URL_PART = "/unit_econ"

unit_economy_router = APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART)


@unit_economy_router.post(UNIT_ECON_URL_PART + '/calculate/', response_model=UnitEconomyResultObject)
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


@unit_economy_router.post(UNIT_ECON_URL_PART + '/save/', response_model=RequestInfo)
def save(unit_economy_save_item: UnitEconomySaveObject,
         access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    request_to_save: UnitEconomyRequestObject = unit_economy_save_item.request
    info_to_save: RequestInfo = unit_economy_save_item.info
    result_to_save: UnitEconomyResultObject = unit_economy_save_item.result
    request_time: datetime
    if info_to_save.timestamp == 0:
        request_time = datetime.utcnow()
    else:
        request_time = datetime.fromtimestamp(info_to_save.timestamp)
    info: JRequestInfo = JRequestInfo(info_to_save.id,
                                      request_time,
                                      info_to_save.name)
    request: UnitEconomyRequest = pydantic_to_jorm(UnitEconomyRequest, request_to_save)
    result = pydantic_to_jorm(UnitEconomyResult, result_to_save)
    request_id = request_handler.save_unit_economy_request(request, result, info, user)

    info_to_save.id = request_id
    info_to_save.timestamp = info.date.timestamp()

    return info_to_save


@unit_economy_router.get(UNIT_ECON_URL_PART + '/get-all/', response_model=list[UnitEconomySaveObject])
def get_all(access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    unit_economy_results_list = request_handler.get_all_request_results(user, UnitEconomyRequest, UnitEconomyResult)
    result = [
        UnitEconomySaveObject.parse_obj({
            "request": jorm_to_pydantic(unit_economy_result[0], UnitEconomyRequestObject),
            "result": jorm_to_pydantic(unit_economy_result[1], UnitEconomyResultObject),
            "info": RequestInfo.parse_obj({
                "name": unit_economy_result[2].name,
                "id": unit_economy_result[2].id,
                "timestamp": unit_economy_result[2].date.timestamp()
            })
        }) for unit_economy_result in unit_economy_results_list
    ]
    return result


@unit_economy_router.post(UNIT_ECON_URL_PART + '/delete/')
def delete(request_id: int,
           access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    request_handler.delete_request(request_id, user, UnitEconomyRequest)
