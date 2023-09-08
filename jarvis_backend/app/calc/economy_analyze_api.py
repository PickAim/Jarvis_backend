from fastapi import Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, UserPrivilege
from jorm.market.service import RequestInfo, SimpleEconomySaveObject

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import SavableCalculationRequestAPI
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.sessions.dependencies import request_handler_depend, session_depend, session_controller_depend
from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.sessions.request_items import SimpleEconomyRequestModel, SimpleEconomyResultModel, \
    SimpleEconomySaveModel, RequestInfoModel, BasicDeleteRequestModel
from jarvis_backend.support.utils import pydantic_to_jorm, transform_info, jorm_to_pydantic


class EconomyAnalyzeAPI(SavableCalculationRequestAPI):
    UNIT_ECON_URL_PART = "/unit-econ"
    router = SavableCalculationRequestAPI._router()
    router.prefix += UNIT_ECON_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=tuple[SimpleEconomyResultModel, SimpleEconomyResultModel])
    def calculate(request_data: SimpleEconomyRequestModel,
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        niche: Niche = session_controller.get_niche(request_data.niche_id,
                                                    request_data.category_id,
                                                    request_data.marketplace_id)
        if niche is None:
            raise JarvisExceptions.INCORRECT_NICHE
        warehouse: Warehouse = \
            session_controller.get_warehouse(request_data.warehouse_name, request_data.marketplace_id)
        result = CalculationController.calc_unit_economy(request_data, niche, warehouse)
        return result

    @staticmethod
    @router.post('/save/', response_model=RequestInfoModel)
    def save(request_data: SimpleEconomySaveModel,
             access_token: str = Depends(access_token_correctness_post_depend),
             session=Depends(session_depend)) -> RequestInfoModel:
        session_controller = session_controller_depend(session)
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            marketplace_id=request_data.user_result[0].marketplace_id,
            user_id=user.user_id
        )
        to_save = EconomyAnalyzeAPI.convert_save_object(request_data)
        to_save.info.id = request_handler.save_simple_economy_request(to_save, user.user_id)
        return jorm_to_pydantic(to_save.info, RequestInfoModel)

    @staticmethod
    def convert_save_object(save_model: SimpleEconomySaveModel) \
            -> SimpleEconomySaveObject:
        info: RequestInfo = transform_info(save_model.info)
        to_save = pydantic_to_jorm(SimpleEconomySaveObject, save_model)
        to_save.info = info
        return to_save

    @staticmethod
    @router.post('/get-all/', response_model=list[SimpleEconomySaveModel])
    def get_all(access_token: str = Depends(access_token_correctness_post_depend),
                session=Depends(session_depend)):
        # TODO think about other MPs
        session_controller = session_controller_depend(session)
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            user_id=user.user_id
        )
        simple_results = request_handler.get_all_simple_economy_results(user.user_id)
        result = [
            jorm_to_pydantic(simple_result, SimpleEconomySaveModel)
            for simple_result in simple_results
        ]
        return result

    @staticmethod
    @router.post('/delete/')
    def delete(request_data: BasicDeleteRequestModel,
               access_token: str = Depends(access_token_correctness_post_depend),
               session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        user: User = EconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            user_id=user.user_id
        )
        request_handler.delete_simple_economy_request(request_data.request_id, user.user_id)
