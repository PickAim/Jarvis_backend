from datetime import datetime

from fastapi import Depends
from jorm.market.infrastructure import Niche
from jorm.market.person import User, UserPrivilege
from pydantic import BaseModel

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import SavableCalculationRequestAPI, CalculationRequestAPI
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend, request_handler_depend
from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.sessions.request_items import RequestInfo, FrequencyRequest, FrequencyResult, FrequencySaveObject, \
    NicheCharacteristicsResultObject, NicheRequest, BasicDeleteRequestObject, GreenTradeZoneCalculateResultObject
from jarvis_backend.support.types import JFrequencySaveObject
from jarvis_backend.support.utils import convert_save_objects_to_jorm, convert_save_objects_to_pydantic


def _check_ang_get_niche(request_data: NicheRequest, session_controller: JarvisSessionController) -> Niche:
    # TODO switch to relaxed niche as soon as implemented
    niche = session_controller.get_niche(request_data.niche,
                                         request_data.category_id,
                                         request_data.marketplace_id)
    if niche is None:
        raise JarvisExceptions.INCORRECT_NICHE
    return niche


class NicheFrequencyAPI(SavableCalculationRequestAPI):
    NICHE_FREQUENCY_URL_PART = "/niche-frequency"
    router = SavableCalculationRequestAPI._router()
    router.prefix += NICHE_FREQUENCY_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=FrequencyResult)
    def calculate(request_data: FrequencyRequest,
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)) -> FrequencyResult:
        NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        niche = _check_ang_get_niche(request_data, session_controller)
        result = CalculationController.calc_frequencies(niche)
        converted_result = FrequencyResult.model_validate(result)
        return converted_result

    @staticmethod
    @router.post('/save/', response_model=RequestInfo)
    def save(request_data: FrequencySaveObject,
             access_token: str = Depends(access_token_correctness_post_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)) -> RequestInfo:
        user: User = NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        jorm_save_object: JFrequencySaveObject = convert_save_objects_to_jorm(request_data, JFrequencySaveObject)
        return SavableCalculationRequestAPI.save_and_return_info(request_handler, user.user_id, jorm_save_object)

    @staticmethod
    @router.post('/get-all/', response_model=list[FrequencySaveObject])
    def get_all(access_token: str = Depends(access_token_correctness_post_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)) -> list[FrequencySaveObject]:
        user: User = NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        frequencies_results_list = request_handler.get_all_request_results(user.user_id, JFrequencySaveObject)
        result = [
            convert_save_objects_to_pydantic(FrequencySaveObject, *frequency_result)
            for frequency_result in frequencies_results_list
        ]
        return result

    @staticmethod
    @router.post('/delete/')
    def delete(request_data: BasicDeleteRequestObject,
               access_token: str = Depends(access_token_correctness_post_depend),
               session_controller: JarvisSessionController = Depends(session_controller_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        request_handler.delete_request(request_data.request_id, user.user_id, JFrequencySaveObject)


class NicheCharacteristicsAPI(CalculationRequestAPI):
    NICHE_CHARACTERISTICS_URL_PART = "/niche-characteristics"

    router = CalculationRequestAPI._router()
    router.prefix += NICHE_CHARACTERISTICS_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=NicheCharacteristicsResultObject)
    def calculate(request_data: NicheRequest, access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)) \
            -> NicheCharacteristicsResultObject:
        NicheCharacteristicsAPI.check_and_get_user(session_controller, access_token)
        niche = _check_ang_get_niche(request_data, session_controller)
        result = CalculationController.calc_niche_characteristics(niche)
        return result


class TempResult(BaseModel):
    green: GreenTradeZoneCalculateResultObject
    freq: dict[str, list[int]]


class GreenTradeZoneAPI(CalculationRequestAPI):
    GREEN_TRADE_ZONE_URL_PART = "/green-trade-zone"

    router = CalculationRequestAPI._router()
    router.prefix += GREEN_TRADE_ZONE_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=TempResult)
    def calculate(request_data: NicheRequest, access_token: str = Depends(access_token_correctness_post_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        GreenTradeZoneAPI.check_and_get_user(session_controller, access_token)
        niche = _check_ang_get_niche(request_data, session_controller)
        frequency_graph = CalculationController.calc_frequencies(niche)
        result = CalculationController.calc_green_zone(niche, datetime.utcnow())
        return TempResult.model_validate({
            "green": result,
            "freq": frequency_graph
        })
