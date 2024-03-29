from fastapi import APIRouter, Depends
from jarvis_factory.factories.jdb import JDBClassesFactory
from jorm.market.person import User
from starlette.responses import JSONResponse

from jarvis_backend.app.constants import ACCESS_TOKEN_USAGE_URL_PART
from jarvis_backend.app.tags import USER_TAG
from jarvis_backend.app.tokens.dependencies import access_token_correctness_post_depend
from jarvis_backend.controllers.cookie import CookieHandler
from jarvis_backend.sessions.dependencies import session_controller_depend, session_depend
from jarvis_backend.sessions.request_items import AddApiKeyModel, BasicMarketplaceInfoModel, GetAllProductsModel
from jarvis_backend.support.request_api import RequestAPI


class UserAPI(RequestAPI):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART, tags=[USER_TAG])

    router = _router()

    @staticmethod
    @router.post('/add-marketplace-api-key/')
    def add_marketplace_api_key(request_data: AddApiKeyModel,
                                access_token: str = Depends(access_token_correctness_post_depend),
                                session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        user: User = session_controller.get_user(access_token)
        if request_data.marketplace_id in user.marketplace_keys:
            session_controller.delete_marketplace_api_key(request_data, user.user_id)
        session_controller.add_marketplace_api_key(request_data, user.user_id)

    @staticmethod
    @router.post('/get-all-marketplace-api-keys/', response_model=dict[int, str])
    def get_all_marketplace_api_keys(access_token: str = Depends(access_token_correctness_post_depend),
                                     session=Depends(session_depend)) -> dict[int, str]:
        session_controller = session_controller_depend(session)
        user: User = session_controller.get_user(access_token)
        return user.marketplace_keys

    @staticmethod
    @router.post('/delete-marketplace-api-key/')
    def delete_marketplace_api_key(request_data: BasicMarketplaceInfoModel,
                                   access_token: str = Depends(access_token_correctness_post_depend),
                                   session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        user: User = session_controller.get_user(access_token)
        session_controller.delete_marketplace_api_key(request_data, user.user_id)

    @staticmethod
    @router.post('/get-all-in-marketplace-user-products/')  # TODO add response model
    def get_all_in_marketplace_user_products(request_data: GetAllProductsModel,
                                             access_token: str = Depends(access_token_correctness_post_depend),
                                             session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        user: User = session_controller.get_user(access_token)
        jorm_changer = JDBClassesFactory.create_jorm_changer(session,
                                                             marketplace_id=request_data.marketplace_id,
                                                             user_id=user.user_id)
        jorm_changer.load_user_products(user_id=user.user_id, marketplace_id=request_data.marketplace_id)
        user_products = session_controller.get_products_by_user(user.user_id, request_data.marketplace_id)
        return {
            product_id: {
                "global_id": user_products[product_id].global_id,
                "name": user_products[product_id].name,
                "category_niche_list": user_products[product_id].category_niche_list,
                "cost": user_products[product_id].cost,
                "rating": user_products[product_id].rating,
                "seller": user_products[product_id].seller,
                "brand": user_products[product_id].brand,
            }
            for product_id in user_products
        }

    @staticmethod
    @router.post('/get-all-user-products/', response_model=dict[int, dict[int, dict]])
    def get_all_user_products(access_token: str = Depends(access_token_correctness_post_depend),
                              session=Depends(session_depend)) -> dict[int, dict]:
        session_controller = session_controller_depend(session)
        id_to_marketplace = session_controller.get_all_marketplaces()
        return {
            marketplace_id: UserAPI.get_all_in_marketplace_user_products(
                GetAllProductsModel.model_validate({
                    "marketplace_id": marketplace_id
                }),
                access_token=access_token,
                session=session
            )
            for marketplace_id in id_to_marketplace
        }

    @staticmethod
    @router.post('/delete-account/')
    def delete_account(access_token: str = Depends(access_token_correctness_post_depend),
                       session=Depends(session_depend)):
        session_controller = session_controller_depend(session)
        user: User = session_controller.get_user(access_token)
        session_controller.delete_account(user.user_id)
        response = JSONResponse(content="deleted")
        return CookieHandler.delete_all_cookie(response)
