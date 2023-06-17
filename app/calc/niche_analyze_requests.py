from fastapi import Depends

from app.calc.calculation_request_api import CalculationRequestAPI
from app.handlers import calculation_controller
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController, RequestHandler
from sessions.request_items import RequestInfo
from support.request_api import post, get


class NicheFrequencyAPI(CalculationRequestAPI):
    NICHE_FREQUENCY_URL_PART = "/niche-frequency"
    router = CalculationRequestAPI._router()
    router.prefix += NICHE_FREQUENCY_URL_PART

    @staticmethod
    @post(router, '/save/', response_model=dict[str, list[int] | list[int]])
    def calculate(niche_name: str, category_name, marketplace_id: int,
                  access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        niche = session_controller.get_niche(niche_name, category_name, marketplace_id)
        result = calculation_controller.calc_frequencies(niche)
        return {
            'x': result[0],
            'y': result[1]
        }

    @staticmethod
    @post(router, '/save/', response_model=RequestInfo)
    def save(access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        pass

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
