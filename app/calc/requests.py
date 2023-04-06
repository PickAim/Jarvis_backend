from fastapi import APIRouter, Depends
from jorm.market.infrastructure import Niche
from jorm.market.person import User

from app.constants import ACCESS_TOKEN_USAGE_URL_PART
from app.handlers import session_controller, calculation_controller
from app.tokens.dependencies import access_token_correctness_depend

calc_router = APIRouter(prefix=ACCESS_TOKEN_USAGE_URL_PART)


@calc_router.get('/jorm_data/')
def upload_data(niche_name: str, _: str = Depends(access_token_correctness_depend)):
    niche: Niche = session_controller.get_niche(niche_name)
    x, y = calculation_controller.calc_frequencies(niche)
    return {'x': x, 'y': y}


@calc_router.get('/save_request/')
def save_request_to_history(request_json: str,
                            access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    session_controller.save_request(request_json, user)
