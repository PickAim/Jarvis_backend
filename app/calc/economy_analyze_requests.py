from fastapi import Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, UserPrivilege
from jorm.market.service import UnitEconomyRequest

from app.calc.calculation import CalculationController
from app.calc.calculation_request_api import SavableCalculationRequestAPI
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController
from sessions.request_handler import RequestHandler
from sessions.request_items import UnitEconomyRequestObject, UnitEconomyResultObject, UnitEconomySaveObject, \
    RequestInfo
from support.request_api import post, get
from support.types import JEconomySaveObject
from support.utils import jorm_to_pydantic, convert_save_objects


class EconomyAnalyzeAPI(SavableCalculationRequestAPI):
    UNIT_ECON_URL_PART = "/unit-econ"
    router = SavableCalculationRequestAPI._router()
    router.prefix += UNIT_ECON_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @post(router, '/calculate/', response_model=UnitEconomyResultObject)
    def calculate(unit_economy_item: UnitEconomyRequestObject,
                  access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        niche: Niche = session_controller.get_niche(unit_economy_item.niche,
                                                    unit_economy_item.category, unit_economy_item.marketplace_id)
        warehouse: Warehouse = session_controller.get_warehouse(unit_economy_item.warehouse_name)
        result = CalculationController.calc_unit_economy(unit_economy_item, niche, warehouse, user)
        return result

    @staticmethod
    @post(router, '/save/', response_model=RequestInfo)
    def save(unit_economy_save_item: UnitEconomySaveObject,
             access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        jorm_economy_save_object: JEconomySaveObject = convert_save_objects(unit_economy_save_item, JEconomySaveObject)
        return SavableCalculationRequestAPI.save_and_return_info(request_handler, user.user_id,
                                                                 jorm_economy_save_object)

    @staticmethod
    @get(router, '/get-all/', response_model=list[UnitEconomySaveObject])
    def get_all(access_token: str = Depends(access_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        unit_economy_results_list = request_handler.get_all_request_results(user.user_id, JEconomySaveObject)
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
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler.delete_request(request_id, user.user_id, UnitEconomyRequest)
