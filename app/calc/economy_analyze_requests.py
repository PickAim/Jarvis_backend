from fastapi import Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User
from jorm.market.service import UnitEconomyRequest, UnitEconomyResult

from app.calc.calculation_request_api import CalculationRequestAPI
from app.handlers import calculation_controller
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController, RequestHandler
from sessions.request_items import UnitEconomyRequestObject, UnitEconomyResultObject, UnitEconomySaveObject, \
    RequestInfo
from support.request_api import post, get
from support.utils import pydantic_to_jorm, jorm_to_pydantic


class EconomyAnalyzeAPI(CalculationRequestAPI):
    UNIT_ECON_URL_PART = "/unit-econ"
    router = CalculationRequestAPI._router()
    router.prefix += UNIT_ECON_URL_PART

    @staticmethod
    @post(router, '/calculate/', response_model=UnitEconomyResultObject)
    def calculate(unit_economy_item: UnitEconomyRequestObject,
                  access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = session_controller.get_user(access_token)
        niche: Niche = session_controller.get_niche(unit_economy_item.niche,
                                                    unit_economy_item.category, unit_economy_item.marketplace_id)
        warehouse: Warehouse = session_controller.get_warehouse(unit_economy_item.warehouse_name)
        result = calculation_controller.calc_unit_economy(unit_economy_item.buy, unit_economy_item.pack, niche,
                                                          warehouse, user, unit_economy_item.transit_price,
                                                          unit_economy_item.transit_count,
                                                          unit_economy_item.transit_price)
        return result

    @staticmethod
    @post(router, '/save/', response_model=RequestInfo)
    def save(unit_economy_save_item: UnitEconomySaveObject,
             access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = session_controller.get_user(access_token)
        request_to_save, result_to_save, info_to_save = (
            unit_economy_save_item.request, unit_economy_save_item.request, unit_economy_save_item.info)

        request: UnitEconomyRequest = pydantic_to_jorm(UnitEconomyRequest, request_to_save)
        result = pydantic_to_jorm(UnitEconomyResult, result_to_save)
        return CalculationRequestAPI.save_and_return_info(request_handler, user.user_id,
                                                          request, result, info_to_save, request_to_save.marketplace_id)

    @staticmethod
    @get(router, '/get-all/', response_model=list[UnitEconomySaveObject])
    def get_all(access_token: str = Depends(access_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = session_controller.get_user(access_token)
        unit_economy_results_list = request_handler.get_all_request_results(user.user_id, UnitEconomyRequest,
                                                                            UnitEconomyResult)
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

    @staticmethod
    @get(router, '/delete/')
    def delete(request_id: int,
               access_token: str = Depends(access_token_correctness_depend),
               session_controller: JarvisSessionController = Depends(session_controller_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = session_controller.get_user(access_token)
        request_handler.delete_request(request_id, user.user_id, UnitEconomyRequest)
