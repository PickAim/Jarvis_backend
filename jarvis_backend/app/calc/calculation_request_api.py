from abc import abstractmethod

from fastapi import Depends, APIRouter

from jarvis_backend.app.constants import ACCESS_TOKEN_USAGE_URL_PART
from jarvis_backend.app.tags import CALCULATION_TAG
from jarvis_backend.app.tokens.dependencies import access_token_correctness_depend
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend, request_handler_depend
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.sessions.request_items import RequestInfo
from jarvis_backend.support.request_api import RequestAPIWithCheck
from jarvis_backend.support.types import JBasicSaveObject


class CalculationRequestAPI(RequestAPIWithCheck):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART, tags=[CALCULATION_TAG])

    @staticmethod
    def save_and_return_info(request_handler: RequestHandler, user_id: int,
                             save_object: JBasicSaveObject) -> RequestInfo:
        request_id = request_handler.save_request(user_id, save_object)
        save_object.info.id = request_id
        return save_object.info

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
