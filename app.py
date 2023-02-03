import uvicorn
from fastapi import FastAPI
from jarvis_calc.utils.calc_utils import get_frequency_stats_with_jorm
from jarvis_calc.utils.margin_calc import unit_economy_calc_with_jorm
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Client
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import PlainTextResponse

from sessions.controllers import JarvisSessionController, BaseRequestItemsHandler
from sessions.request_items import UnitEconomyRequestObject, BaseRequestObject, AuthenticationObject, \
    NicheFrequencyObject, RequestSaveObject

app = FastAPI()
session_controller: JarvisSessionController = JarvisSessionController()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.post('/update_tokens/')
def update_tokens(request_item: BaseRequestObject) -> tuple[str, str, str] | None:
    request_item_handler: BaseRequestItemsHandler = BaseRequestItemsHandler(request_item, "")
    _, update_token, imprint_token = request_item_handler.get_tokens()

    new_access_token, new_update_token = session_controller.update_token(update_token)

    if request_item_handler.is_use_cookie():
        request_item_handler.save_to_cookie()
        return None
    return new_access_token, new_update_token, imprint_token


@app.post('/auth/')
def auth(auth_item: AuthenticationObject) -> tuple[str, str, str] | None:
    request_item_handler: BaseRequestItemsHandler = BaseRequestItemsHandler(auth_item, "")
    _, _, imprint_token = request_item_handler.get_tokens()

    access_token, update_token, imprint_token = \
        session_controller.authenticate_user(auth_item.login, auth_item.password, imprint_token)

    if request_item_handler.is_use_cookie():
        request_item_handler.save_token_to_cookie(access_token, update_token, imprint_token)
    return access_token, update_token, imprint_token


@app.post('/jorm_margin/')
def calc_margin(unit_economy_item: UnitEconomyRequestObject):
    request_item_handler: BaseRequestItemsHandler = BaseRequestItemsHandler(unit_economy_item, "")
    access_token, _, _ = request_item_handler.get_tokens()

    user: User = session_controller.get_user(access_token)

    niche: Niche = session_controller.get_niche(unit_economy_item.niche)
    warehouse: Warehouse = session_controller.get_warehouse(unit_economy_item.warehouse_name)
    result_dict = {}
    if isinstance(user, Client):
        result_dict = unit_economy_calc_with_jorm(unit_economy_item.buy, unit_economy_item.pack, niche,
                                                  warehouse, user, unit_economy_item.transit_price,
                                                  unit_economy_item.transit_count, unit_economy_item.transit_price)
    return result_dict


@app.get('/jorm_data/{niche}')
def upload_data(niche_freq_item: NicheFrequencyObject):
    request_item_handler: BaseRequestItemsHandler = BaseRequestItemsHandler(niche_freq_item, "")
    access_token, _, _ = request_item_handler.get_tokens()

    session_controller.get_user(access_token)

    niche: Niche = session_controller.get_niche(niche_freq_item.niche)
    x, y = get_frequency_stats_with_jorm(niche)
    return {'x': x, 'y': y}


@app.get('/save_request/{request}')
def save_request_to_history(request_save_item: RequestSaveObject):
    request_item_handler: BaseRequestItemsHandler = BaseRequestItemsHandler(request_save_item, "")
    access_token, _, _ = request_item_handler.get_tokens()

    user: User = session_controller.get_user(access_token)

    session_controller.save_request(request_save_item.request_json, user)


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
