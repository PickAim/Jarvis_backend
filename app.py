import os

import uvicorn

from fastapi import FastAPI

from jorm.market.person import User, Client
from jorm.market.infrastructure import Niche, Warehouse

from sessions.controllers import JarvisSessionController
from request_items import UnitEconomyRequestObject, BaseRequestObject, AuthenticationObject

from starlette.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from jarvis_calc.utils.margin_calc import unit_economy_calc_with_jorm
from jarvis_calc.utils.calc_utils import get_frequency_stats_with_jorm


app = FastAPI()
session_controller: JarvisSessionController = JarvisSessionController()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.post('/update_tokens/')
def update_tokens(request_item: BaseRequestObject):
    _, update_token, _ = JarvisSessionController.extract_tokens_from_cookie()
    if update_token is None:
        update_token = request_item.update_token
    return session_controller.update_token(update_token)


@app.post('/auth/')
def auth(auth_item: AuthenticationObject):
    _, _, imprint_token = JarvisSessionController.extract_tokens_from_cookie()
    if imprint_token is None:
        imprint_token = auth_item.imprint_token
    return session_controller.authenticate_user(auth_item.login, auth_item.password, imprint_token)


@app.post('/jorm_margin/')
def calc_margin(unit_economy_item: UnitEconomyRequestObject):
    access_token, _, _ = JarvisSessionController.extract_tokens_from_cookie()
    if access_token is None:
        access_token = unit_economy_item.access_token
    user: User = session_controller.get_user(access_token)
    niche: Niche = session_controller.niche(unit_economy_item.niche)
    warehouse: Warehouse = session_controller.warehouse(unit_economy_item.warehouse_name)
    result_dict = {}
    if isinstance(user, Client):
        result_dict = unit_economy_calc_with_jorm(unit_economy_item.buy, unit_economy_item.pack, niche,
                                                  warehouse, user, unit_economy_item.transit_price,
                                                  unit_economy_item.transit_count, unit_economy_item.transit_price)
    return result_dict


@app.get('/jorm_data/{niche}')
def upload_data(token: bytes, niche: str):
    user = session_controller.get_user(token)
    niche: Niche = session_controller.niche(niche)
    x, y = get_frequency_stats_with_jorm(niche)
    return {'x': x, 'y': y}


@app.get('/save_request/{request}')
def upload_data(token: bytes, request_json: str):
    user = session_controller.get_user(token)
    session_controller.save_request(request_json, user)


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
