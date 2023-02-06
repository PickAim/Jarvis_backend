import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from jarvis_calc.utils.calc_utils import get_frequency_stats_with_jorm
from jarvis_calc.utils.margin_calc import unit_economy_calc_with_jorm
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Client
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import PlainTextResponse

from auth.tokens.token_control import TokenController
from sessions.controllers import JarvisSessionController, CookieHandler
from sessions.exceptions import JarvisExceptions
from sessions.request_items import UnitEconomyRequestObject, AuthenticationObject

app = FastAPI()
session_controller: JarvisSessionController = JarvisSessionController()


def check_token_correctness(any_session_token: str) -> str:
    session_controller.get_user(any_session_token)
    return any_session_token


def access_token_correctness_depend(access_token: str = None,
                                    cookie_access_token: str = CookieHandler.load_access_token()) -> str:
    if cookie_access_token is not None:
        return check_token_correctness(cookie_access_token)
    elif access_token is not None:
        if TokenController().is_token_expired(access_token):
            raise JarvisExceptions.EXPIRED_TOKEN
        return check_token_correctness(access_token)
    else:
        raise JarvisExceptions.INCORRECT_TOKEN


def update_token_correctness_depend(update_token: str = None,
                                    cookie_update_token: str = CookieHandler.load_update_token()) -> str:
    if cookie_update_token is not None:
        return check_token_correctness(cookie_update_token)
    elif update_token is not None:
        return check_token_correctness(update_token)
    else:
        raise JarvisExceptions.INCORRECT_TOKEN


def imprint_token_correctness_depend(imprint_token: str = None,
                                     cookie_imprint_token: str = CookieHandler.load_imprint_token()) -> str | None:
    if cookie_imprint_token is not None:
        return cookie_imprint_token
    elif imprint_token is not None:
        return imprint_token
    else:
        return None


@app.post("/delete_all_cookie/")
def delete_cookie():
    response = JSONResponse(content="deleted")
    return CookieHandler.delete_all_cookie(response)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.get('/update/update_all_tokens')
def update_tokens(update_token: str = Depends(update_token_correctness_depend)):
    new_access_token, new_update_token = session_controller.update_token(update_token)
    response: JSONResponse = JSONResponse(content={
        "access_token": new_access_token,
        "update_token": new_update_token,
    })
    CookieHandler.save_access_token(response, new_access_token)
    CookieHandler.save_update_token(response, new_update_token)
    return response


@app.post('/auth/')
def auth(auth_item: AuthenticationObject,
         imprint_token: str = Depends(imprint_token_correctness_depend)):
    new_access_token, new_update_token, new_imprint_token = \
        session_controller.authenticate_user(auth_item.login, auth_item.password, imprint_token)
    response: JSONResponse = JSONResponse(content={
        "access_token": new_access_token,
        "update_token": new_update_token,
        "imprint_token": new_imprint_token
    })
    CookieHandler.save_access_token(response, new_access_token)
    CookieHandler.save_update_token(response, new_update_token)
    CookieHandler.save_imprint_token(response, new_imprint_token)
    return response


@app.post('/access/jorm_margin/')
def calc_margin(unit_economy_item: UnitEconomyRequestObject,
                access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    niche: Niche = session_controller.get_niche(unit_economy_item.niche)
    warehouse: Warehouse = session_controller.get_warehouse(unit_economy_item.warehouse_name)
    result_dict = {}
    if isinstance(user, Client):
        result_dict = unit_economy_calc_with_jorm(unit_economy_item.buy, unit_economy_item.pack, niche,
                                                  warehouse, user, unit_economy_item.transit_price,
                                                  unit_economy_item.transit_count, unit_economy_item.transit_price)
    return result_dict


@app.get('/access/jorm_data/')
def upload_data(niche_name: str, _: str = Depends(access_token_correctness_depend)):
    niche: Niche = session_controller.get_niche(niche_name)
    x, y = get_frequency_stats_with_jorm(niche)
    return {'x': x, 'y': y}


@app.get('/access/save_request/')
def save_request_to_history(request_json: str,
                            access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    session_controller.save_request(request_json, user)


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
