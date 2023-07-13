from abc import abstractmethod

from fastapi import Depends, APIRouter

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.tags import CALCULATION_TAG
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController
from sessions.request_handler import RequestHandler
from sessions.request_items import RequestInfo
from support.request_api import RequestAPIWithCheck
from support.types import JBasicSaveObject


class CalculationRequestAPI(RequestAPIWithCheck):

    @staticmethod
    def save_and_return_info(request_handler: RequestHandler, user_id: int,
                             save_object: JBasicSaveObject) -> RequestInfo:
        request_id = request_handler.save_request(user_id, save_object)
        save_object.info.id = request_id
        return save_object.info

    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART, tags=[CALCULATION_TAG])

    @staticmethod
    @abstractmethod
    def calculate(access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        pass


class SavableCalculationRequestAPI(CalculationRequestAPI):
    @staticmethod
    @abstractmethod
    def save(access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        pass

    @staticmethod
    @abstractmethod
    def get_all(access_token: str = Depends(access_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        pass

    @staticmethod
    @abstractmethod
    def delete(request_id: int,
               access_token: str = Depends(access_token_correctness_depend),
               session_controller: JarvisSessionController = Depends(session_controller_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        pass
