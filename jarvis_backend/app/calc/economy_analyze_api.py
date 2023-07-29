from fastapi import Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, UserPrivilege

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import SavableCalculationRequestAPI
from jarvis_backend.app.tokens.dependencies import access_token_correctness_depend
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend, request_handler_depend
from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.sessions.request_items import UnitEconomyRequestObject, UnitEconomyResultObject, \
    UnitEconomySaveObject, \
    RequestInfo
from jarvis_backend.support.types import JEconomySaveObject
from jarvis_backend.support.utils import convert_save_objects_to_jorm, convert_save_objects_to_pydantic


class EconomyAnalyzeAPI(SavableCalculationRequestAPI):
    UNIT_ECON_URL_PART = "/unit-econ"
    router = SavableCalculationRequestAPI._router()
    router.prefix += UNIT_ECON_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=UnitEconomyResultObject)
    def calculate(unit_economy_item: UnitEconomyRequestObject,
                  access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        # TODO get_niche
        niche: Niche = session_controller.get_relaxed_niche(unit_economy_item.niche,
                                                            unit_economy_item.category_id,
                                                            unit_economy_item.marketplace_id)
        if niche is None:
            raise JarvisExceptions.INCORRECT_NICHE
        warehouse: Warehouse = \
            session_controller.get_warehouse(unit_economy_item.warehouse_name, unit_economy_item.marketplace_id)
        result = CalculationController.calc_unit_economy(unit_economy_item, niche, warehouse, user)
        return result

    @staticmethod
    @router.post('/save/', response_model=RequestInfo)
    def save(unit_economy_save_item: UnitEconomySaveObject,
             access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        jorm_economy_save_object: JEconomySaveObject = convert_save_objects_to_jorm(unit_economy_save_item,
                                                                                    JEconomySaveObject)
        return SavableCalculationRequestAPI.save_and_return_info(request_handler, user.user_id,
                                                                 jorm_economy_save_object)

    @staticmethod
    @router.get('/get-all/', response_model=list[UnitEconomySaveObject])
    def get_all(access_token: str = Depends(access_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        unit_economy_results_list = request_handler.get_all_request_results(user.user_id, JEconomySaveObject)
        result = [
            convert_save_objects_to_pydantic(UnitEconomySaveObject, *unit_economy_result)
            for unit_economy_result in unit_economy_results_list
        ]
        return result

    @staticmethod
    @router.get('/delete/')
    def delete(request_id: int,
               access_token: str = Depends(access_token_correctness_depend),
               session_controller: JarvisSessionController = Depends(session_controller_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler.delete_request(request_id, user.user_id, JEconomySaveObject)
