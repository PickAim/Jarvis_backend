from fastapi import Depends
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, UserPrivilege
from jorm.market.service import RequestInfo, SimpleEconomySaveObject, TransitEconomySaveObject, SimpleEconomyRequest, \
    TransitEconomyRequest
from jorm.support.calculation import SimpleEconomyResult, TransitEconomyResult

from jarvis_backend.app.calc.calculation import CalculationController
from jarvis_backend.app.calc.calculation_request_api import SavableCalculationRequestAPI
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.sessions.dependencies import request_handler_depend, session_depend, session_controller_depend
from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.sessions.request_handler import RequestHandler
from jarvis_backend.sessions.request_items import SimpleEconomyRequestModel, SimpleEconomyResultModel, \
    SimpleEconomySaveModel, RequestInfoModel, BasicDeleteRequestModel, TransitEconomyRequestModel, \
    TransitEconomyResultModel, TransitEconomySaveModel
from jarvis_backend.support.utils import pydantic_to_jorm, transform_info, jorm_to_pydantic


class SimpleEconomyAnalyzeAPI(SavableCalculationRequestAPI):
    SIMPLE_ECON_URL_PART = "/simple-unit-econ"
    router = SavableCalculationRequestAPI._router()
    router.prefix += SIMPLE_ECON_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=tuple[SimpleEconomyResultModel, SimpleEconomyResultModel])
    def calculate(request_data: SimpleEconomyRequestModel,
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        SimpleEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        niche: Niche = session_controller.get_niche(request_data.niche_id)
        if niche is None:
            raise JarvisExceptions.INCORRECT_NICHE
        target_warehouse: Warehouse = \
            session_controller.get_warehouse(request_data.target_warehouse_name, request_data.marketplace_id)
        result = CalculationController.calc_simple_economy(request_data, niche, target_warehouse)
        return result

    @staticmethod
    @router.post('/save/', response_model=RequestInfoModel)
    def save(request_data: SimpleEconomySaveModel,
             access_token: str = Depends(access_token_correctness_post_depend),
             session=Depends(session_depend)) -> RequestInfoModel:
        session_controller = session_controller_depend(session)
        user: User = SimpleEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            marketplace_id=request_data.user_result[0].marketplace_id,
            user_id=user.user_id
        )
        to_save = SimpleEconomyAnalyzeAPI.convert_save_object(request_data)
        to_save.info.id = request_handler.save_simple_economy_request(to_save, user.user_id)
        return jorm_to_pydantic(to_save.info, RequestInfoModel)

    @staticmethod
    def convert_save_object(save_model: SimpleEconomySaveModel) \
            -> SimpleEconomySaveObject:
        info: RequestInfo = transform_info(save_model.info)
        economy_request = pydantic_to_jorm(SimpleEconomyRequest, save_model.user_result[0])
        user_result = pydantic_to_jorm(SimpleEconomyResult, save_model.user_result[1])
        recommended_result = pydantic_to_jorm(SimpleEconomyResult, save_model.recommended_result[1])
        to_save = SimpleEconomySaveObject(info=info,
                                          user_result=(economy_request, user_result),
                                          recommended_result=(economy_request, recommended_result))
        return to_save

    @staticmethod
    @router.post('/get-all/', response_model=list[SimpleEconomySaveModel])
    def get_all(access_token: str = Depends(access_token_correctness_post_depend),
                session=Depends(session_depend)):
        # TODO think about other MPs
        session_controller = session_controller_depend(session)
        user: User = SimpleEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
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
        user: User = SimpleEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            user_id=user.user_id
        )
        request_handler.delete_simple_economy_request(request_data.request_id, user.user_id)


class TransitEconomyAnalyzeAPI(SavableCalculationRequestAPI):
    TRANSIT_ECON_URL_PART = "/transit-unit-econ"
    router = SavableCalculationRequestAPI._router()
    router.prefix += TRANSIT_ECON_URL_PART

    @classmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        return UserPrivilege.BASIC

    @staticmethod
    @router.post('/calculate/', response_model=tuple[TransitEconomyResultModel, TransitEconomyResultModel])
    def calculate(request_data: TransitEconomyRequestModel,
                  access_token: str = Depends(access_token_correctness_post_depend),
                  session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        user: User = TransitEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        niche: Niche = session_controller.get_niche(request_data.niche_id)
        if niche is None:
            raise JarvisExceptions.INCORRECT_NICHE
        target_warehouse: Warehouse = \
            session_controller.get_warehouse(request_data.target_warehouse_name, request_data.marketplace_id)
        result = CalculationController.calc_transit_economy(request_data, user, niche, target_warehouse)
        return result

    @staticmethod
    @router.post('/save/', response_model=RequestInfoModel)
    def save(request_data: TransitEconomySaveModel,
             access_token: str = Depends(access_token_correctness_post_depend),
             session=Depends(session_depend)) -> RequestInfoModel:
        session_controller = session_controller_depend(session)
        user: User = TransitEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            marketplace_id=request_data.user_result[0].marketplace_id,
            user_id=user.user_id
        )
        to_save = TransitEconomyAnalyzeAPI.convert_save_object(request_data)
        to_save.info.id = request_handler.save_transit_economy_request(to_save, user.user_id)
        return jorm_to_pydantic(to_save.info, RequestInfoModel)

    @staticmethod
    def convert_save_object(save_model: TransitEconomySaveModel) \
            -> TransitEconomySaveObject:
        info: RequestInfo = transform_info(save_model.info)
        economy_request = pydantic_to_jorm(TransitEconomyRequest, save_model.user_result[0])
        user_result = pydantic_to_jorm(TransitEconomyResult, save_model.user_result[1])
        recommended_result = pydantic_to_jorm(TransitEconomyResult, save_model.recommended_result[1])
        to_save = TransitEconomySaveObject(info=info,
                                           user_result=(economy_request, user_result),
                                           recommended_result=(economy_request, recommended_result))
        return to_save

    @staticmethod
    @router.post('/get-all/', response_model=list[TransitEconomySaveModel])
    def get_all(access_token: str = Depends(access_token_correctness_post_depend),
                session=Depends(session_depend)):
        # TODO think about other MPs
        session_controller = session_controller_depend(session)
        user: User = TransitEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            user_id=user.user_id
        )
        transit_results = request_handler.get_all_transit_economy_results(user.user_id)
        result = [
            jorm_to_pydantic(transit_result, TransitEconomySaveModel)
            for transit_result in transit_results
        ]
        return result

    @staticmethod
    @router.post('/delete/')
    def delete(request_data: BasicDeleteRequestModel,
               access_token: str = Depends(access_token_correctness_post_depend),
               session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        user: User = TransitEconomyAnalyzeAPI.check_and_get_user(session_controller, access_token)
        request_handler: RequestHandler = request_handler_depend(
            session=session,
            user_id=user.user_id
        )
        request_handler.delete_transit_economy_request(request_data.request_id, user.user_id)
