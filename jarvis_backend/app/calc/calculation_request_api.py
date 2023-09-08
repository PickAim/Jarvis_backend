from abc import abstractmethod

from fastapi import Depends, APIRouter

from jarvis_backend.app.constants import ACCESS_TOKEN_USAGE_URL_PART
from jarvis_backend.app.tags import CALCULATION_TAG
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.sessions.dependencies import request_handler_depend, session_depend
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.support.request_api import RequestAPIWithCheck


class CalculationRequestAPI(RequestAPIWithCheck):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART, tags=[CALCULATION_TAG])

    @staticmethod
    @abstractmethod
    def calculate(access_token: str = Depends(access_token_correctness_post_depend), session=Depends(session_depend)):
        pass


class SavableCalculationRequestAPI(CalculationRequestAPI):
    @staticmethod
    @abstractmethod
    def save(access_token: str = Depends(access_token_correctness_post_depend),
             session=Depends(session_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        pass

    @staticmethod
    @abstractmethod
    def get_all(access_token: str = Depends(access_token_correctness_post_depend),
                session=Depends(session_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        pass

    @staticmethod
    @abstractmethod
    def delete(request_id: int,
               access_token: str = Depends(access_token_correctness_post_depend), session=Depends(session_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        pass
