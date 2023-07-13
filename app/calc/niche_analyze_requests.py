from fastapi import Depends
from jorm.market.person import User, UserPrivilege

from app.calc.calculation import CalculationController
from app.calc.calculation_request_api import SavableCalculationRequestAPI, CalculationRequestAPI
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController
from sessions.request_handler import RequestHandler
from sessions.request_items import RequestInfo, FrequencyRequest, FrequencyResult, FrequencySaveObject, \
    NicheCharacteristicsResultObject, NicheRequest
from support.request_api import post, get
from support.types import JFrequencySaveObject
from support.utils import convert_save_objects_to_jorm, convert_save_objects_to_pydantic


class NicheFrequencyAPI(SavableCalculationRequestAPI):
    NICHE_FREQUENCY_URL_PART = "/niche-frequency"
    router = SavableCalculationRequestAPI._router()
    router.prefix += NICHE_FREQUENCY_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @post(router, '/calculate/', response_model=FrequencyResult)
    def calculate(frequency_request: FrequencyRequest,
                  access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        niche = session_controller.get_niche(frequency_request.niche,
                                             frequency_request.category,
                                             frequency_request.marketplace_id)
        result = CalculationController.calc_frequencies(niche)
        converted_result = FrequencyResult.parse_obj(result)
        return converted_result

    @staticmethod
    @post(router, '/save/', response_model=RequestInfo)
    def save(frequency_save_item: FrequencySaveObject,
             access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        jorm_save_object: JFrequencySaveObject = convert_save_objects_to_jorm(frequency_save_item, JFrequencySaveObject)
        return SavableCalculationRequestAPI.save_and_return_info(request_handler, user.user_id, jorm_save_object)

    @staticmethod
    @get(router, '/get-all/', response_model=list[FrequencySaveObject])
    def get_all(access_token: str = Depends(access_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        frequencies_results_list = request_handler.get_all_request_results(user.user_id, JFrequencySaveObject)
        result = [
            convert_save_objects_to_pydantic(FrequencySaveObject, *frequency_result)
            for frequency_result in frequencies_results_list
        ]
        return result

    @staticmethod
    @get(router, '/delete/')
    def delete(request_id: int, access_token: str = Depends(access_token_correctness_depend),
               session_controller: JarvisSessionController = Depends(session_controller_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = NicheFrequencyAPI.check_and_get_user(session_controller, access_token)
        request_handler.delete_request(request_id, user.user_id, JFrequencySaveObject)


class NicheCharacteristicsAPI(CalculationRequestAPI):
    NICHE_CHARACTERISTICS_URL_PART = "/niche-characteristics"

    router = CalculationRequestAPI._router()
    router.prefix += NICHE_CHARACTERISTICS_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=NicheCharacteristicsResultObject)
    def calculate(niche_request: NicheRequest, access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        NicheCharacteristicsAPI.check_and_get_user(session_controller, access_token)
        niche = session_controller.get_niche(niche_request.niche, niche_request.category, niche_request.marketplace_id)
        result = CalculationController.calc_niche_characteristics(niche)
        return result
