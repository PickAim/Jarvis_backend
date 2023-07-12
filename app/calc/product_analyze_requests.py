from datetime import datetime

from fastapi import Depends
from jorm.market.person import User

from app.calc.calculation import CalculationController
from app.calc.calculation_request_api import SavableCalculationRequestAPI
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend, request_handler_depend
from sessions.controllers import JarvisSessionController
from sessions.request_handler import RequestHandler
from sessions.request_items import RequestInfo, ProductDownturnResultObject, \
    ProductDownturnSaveObject
from support.request_api import post, get


class ProductDownturnAPI(SavableCalculationRequestAPI):
    PRODUCT_DOWNTURN_URL_PART = "/product-analyze"
    router = SavableCalculationRequestAPI._router()
    router.prefix += PRODUCT_DOWNTURN_URL_PART

    @staticmethod
    @router.post(PRODUCT_DOWNTURN_URL_PART + '/calculate/', response_model=ProductDownturnResultObject)
    def calculate(access_token: str = Depends(access_token_correctness_depend),
                  session_controller: JarvisSessionController = Depends(session_controller_depend)):
        user: User = session_controller.get_user(access_token)
        user_products = session_controller.get_products_by_user(user.user_id)
        return {
            product.global_id: CalculationController.calc_downturn_days(product, datetime.utcnow())
            for product in user_products
        }

    @staticmethod
    @post(router, '/save/', response_model=RequestInfo)
    def save(product_downturn_save_object: ProductDownturnSaveObject,
             access_token: str = Depends(access_token_correctness_depend),
             session_controller: JarvisSessionController = Depends(session_controller_depend),
             request_handler: RequestHandler = Depends(request_handler_depend)):
        user: User = session_controller.get_user(access_token)
        return SavableCalculationRequestAPI.save_and_return_info(request_handler, user.user_id)

    @staticmethod
    @get(router, '/get-all/', response_model=list[ProductDownturnSaveObject])
    def get_all(access_token: str = Depends(access_token_correctness_depend),
                session_controller: JarvisSessionController = Depends(session_controller_depend),
                request_handler: RequestHandler = Depends(request_handler_depend)):
        pass

    @staticmethod
    def delete(request_id: int, access_token: str = Depends(access_token_correctness_depend),
               session_controller: JarvisSessionController = Depends(session_controller_depend),
               request_handler: RequestHandler = Depends(request_handler_depend)):
        pass
