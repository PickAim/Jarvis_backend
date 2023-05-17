from datetime import datetime

from fastapi import APIRouter, Depends
from jorm.market.person import User

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.handlers import calculation_controller
from app.tokens.dependencies import access_token_correctness_depend, session_controller_depend
from sessions.controllers import JarvisSessionController
from sessions.request_items import UnitEconomyResultObject

PRODUCT_ANALYZE_URL_PART = "/product-analyze"

product_analyze_router = APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART)


@product_analyze_router.post(PRODUCT_ANALYZE_URL_PART + '/calculate/', response_model=UnitEconomyResultObject)
def calculate(access_token: str = Depends(access_token_correctness_depend),
              session_controller: JarvisSessionController = Depends(session_controller_depend)):
    user: User = session_controller.get_user(access_token)
    user_products = session_controller.get_products_by_user(user)
    return {
        product.global_id: calculation_controller.calc_downturn_days(product, datetime.utcnow())
        for product in user_products
    }
