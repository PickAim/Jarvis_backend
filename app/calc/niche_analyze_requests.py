from fastapi import Depends
from jorm.market.person import User

from app.calc.calculation_request_api import CalculationRequestAPI
from app.handlers import calculation_controller
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController, RequestHandler
from sessions.request_items import RequestInfo, FrequencyRequest, FrequencyResult, FrequencySaveObject
from support.request_api import post, get
from support.utils import pydantic_to_jorm


class NicheFrequencyAPI(CalculationRequestAPI):
    NICHE_FREQUENCY_URL_PART = "/niche-frequency"
    router = CalculationRequestAPI._router()
    router.prefix += NICHE_FREQUENCY_URL_PART

    @staticmethod
    @post(router, '/calculate/', response_model=FrequencyResult)
    def calculate(frequency_request: FrequencyRequest,
                  access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        niche = session_controller.get_niche(frequency_request.niche_name,
                                             frequency_request.category_name,
                                             frequency_request.marketplace_id)
        result = calculation_controller.calc_frequencies(niche)
        return {
            'x': result[0],
            'y': result[1]
        }

    @staticmethod
    @post(router, '/save/', response_model=RequestInfo)
    def save(frequency_save_item: FrequencySaveObject,
             access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = session_controller.get_user(access_token)
        request_to_save, result_to_save, info_to_save = (
            frequency_save_item.request, frequency_save_item.request, frequency_save_item.info)

        request: FrequencyRequest = pydantic_to_jorm(FrequencyRequest, request_to_save)
        result = pydantic_to_jorm(FrequencyResult, result_to_save)
        return CalculationRequestAPI.save_and_return_info(request_handler, user.user_id,
                                                          )

    @staticmethod
    @get(router, '/save/', response_model=RequestInfo)
    def get_all(access_token: str = Depends(access_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        pass

    @staticmethod
    def delete(request_id: int, access_token: str = Depends(access_token_correctness_depend),
               session_controller: JarvisSessionController = Depends(session_controller_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        pass
