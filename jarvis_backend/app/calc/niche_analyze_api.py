from datetime import datetime

from fastapi import Depends
from jorm.market.infrastructure import Niche
from jorm.market.person import UserPrivilege
from pydantic import BaseModel

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import CalculationRequestAPI
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend
from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.sessions.request_items import NicheCharacteristicsResultObject, NicheRequest, \
    GreenTradeZoneCalculateResultObject


def _check_ang_get_niche(request_data: NicheRequest, session_controller: JarvisSessionController) -> Niche:
    # TODO switch to relaxed niche as soon as implemented
    niche = session_controller.get_niche(request_data.niche,
                                         request_data.category_id,
                                         request_data.marketplace_id)
    if niche is None:
        raise JarvisExceptions.INCORRECT_NICHE
    return niche


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
        result = CalculationController.calc_green_zone(niche, datetime.utcnow())
        return result
