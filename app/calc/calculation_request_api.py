from abc import abstractmethod
from datetime import datetime

from fastapi import Depends, APIRouter
from jarvis_factory.factories.jorm import JORMClassesFactory
from jorm.market.service import RequestInfo as JRequestInfo

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController, RequestHandler
from sessions.request_items import RequestInfo
from support.request_api import RequestAPI


class CalculationRequestAPI(RequestAPI):
    @staticmethod
    def transform_info(info: RequestInfo) -> JRequestInfo:
        if info.timestamp == 0:
            request_time = datetime.utcnow()
        else:
            request_time = datetime.fromtimestamp(info.timestamp)
        return JRequestInfo(info.id, request_time, info.name)

    @staticmethod
    def save_and_return_info(request_handler: RequestHandler, user_id: int,
                             request, result, info_to_save: RequestInfo, additional_id: int = 0):
        info = CalculationRequestAPI.transform_info(info_to_save)
        try:
            request_id = request_handler.save_request(user_id, request, result, info, additional_id)
        except Exception:
            print("SAVED TO DEFAULT NICHE")
            request.niche = JORMClassesFactory.create_default_niche().name
            request.category = JORMClassesFactory.create_default_category().name
            request.warehouse_name = JORMClassesFactory.create_simple_default_warehouse().name
            request_id = request_handler.save_request(user_id, request, result, info, additional_id)

        info_to_save.id = request_id
        info_to_save.timestamp = info.date.timestamp()
        return info_to_save

    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART)

    @staticmethod
    @abstractmethod
    def calculate(access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        pass

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
