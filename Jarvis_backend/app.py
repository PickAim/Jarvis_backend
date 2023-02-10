import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from jarvis_calc.utils.calc_utils import get_frequency_stats_with_jorm
from jarvis_calc.utils.margin_calc import unit_economy_calc_with_jorm
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Client
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse

from Jarvis_backend.auth import TokenController
from Jarvis_backend.constants import (
    UPDATE_TOKEN_USAGE_URL_PART,
    ACCESS_TOKEN_USAGE_URL_PART,
    ACCESS_TOKEN_NAME,
    UPDATE_TOKEN_NAME,
    IMPRINT_TOKEN_NAME
)
from Jarvis_backend.sessions.controllers import JarvisSessionController, CookieHandler
from Jarvis_backend.sessions.exceptions import JarvisExceptions
from Jarvis_backend.sessions.request_items import UnitEconomyRequestObject, AuthenticationObject, RegistrationObject

app = FastAPI()
session_controller: JarvisSessionController = JarvisSessionController()

origins = [
    "http://localhost",
    "http://localhost:8088",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def check_token_correctness(any_session_token: str, imprint_token: str) -> str:
    if session_controller.check_token_correctness(any_session_token, imprint_token):
        return any_session_token
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


def access_token_correctness_depend(access_token: str = None,
                                    cookie_access_token: str = CookieHandler.load_access_token(),
                                    imprint_token: str = Depends(imprint_token_correctness_depend)) -> str:
    token_to_check: str
    if cookie_access_token is not None:
        token_to_check = cookie_access_token
    elif access_token is not None:
        token_to_check = access_token
    else:
        raise JarvisExceptions.INCORRECT_TOKEN

    if TokenController().is_token_expired(token_to_check):
        raise JarvisExceptions.EXPIRED_TOKEN
    return check_token_correctness(token_to_check, imprint_token)


def update_token_correctness_depend(update_token: str = None,
                                    cookie_update_token: str = CookieHandler.load_update_token(),
                                    imprint_token: str = Depends(imprint_token_correctness_depend)) -> str:
    if cookie_update_token is not None:
        return check_token_correctness(cookie_update_token, imprint_token)
    elif update_token is not None:
        return check_token_correctness(update_token, imprint_token)
    else:
        raise JarvisExceptions.INCORRECT_TOKEN


def save_and_return_session_tokens(access_token: str, update_token: str):
    response: JSONResponse = JSONResponse(content={
        ACCESS_TOKEN_NAME: access_token,
        UPDATE_TOKEN_NAME: update_token,
    })
    CookieHandler.save_access_token(response, access_token)
    CookieHandler.save_update_token(response, update_token)
    return response


def save_and_return_all_tokens(access_token: str, update_token: str, imprint_token: str):
    response: JSONResponse = JSONResponse(content={
        ACCESS_TOKEN_NAME: access_token,
        UPDATE_TOKEN_NAME: update_token,
        IMPRINT_TOKEN_NAME: imprint_token
    })
    CookieHandler.save_access_token(response, access_token)
    CookieHandler.save_update_token(response, update_token)
    CookieHandler.save_imprint_token(response, imprint_token)
    return response


@app.post("/delete_all_cookie/")
def delete_cookie():
    response = JSONResponse(content="deleted")
    return CookieHandler.delete_all_cookie(response)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_, exc):
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


@app.get(UPDATE_TOKEN_USAGE_URL_PART + '/update_all_tokens')
def update_tokens(update_token: str = Depends(update_token_correctness_depend)):
    new_access_token, new_update_token = session_controller.update_token(update_token)
    return save_and_return_session_tokens(new_access_token, new_update_token)


@app.post('/auth/')
def auth(auth_item: AuthenticationObject,
         imprint_token: str = Depends(imprint_token_correctness_depend)):
    new_access_token, new_update_token, new_imprint_token = \
        session_controller.authenticate_user(auth_item.login, auth_item.password, imprint_token)
    return save_and_return_all_tokens(new_access_token, new_update_token, new_imprint_token)


@app.get(ACCESS_TOKEN_USAGE_URL_PART + '/auth/')
def auth_by_token(access_token: str = Depends(access_token_correctness_depend),
                  imprint_token: str = Depends(imprint_token_correctness_depend)):
    new_access_token, new_update_token, new_imprint_token = \
        session_controller.authenticate_user_by_access_token(access_token, imprint_token)
    return save_and_return_all_tokens(new_access_token, new_update_token, new_imprint_token)


@app.get(ACCESS_TOKEN_USAGE_URL_PART + '/log_out/')
def log_out(access_token: str = Depends(access_token_correctness_depend),
            imprint_token: str = Depends(imprint_token_correctness_depend)):
    session_controller.logout(access_token, imprint_token)
    response = JSONResponse(content="deleted")
    CookieHandler.delete_all_cookie(response)
    return response


@app.post('/reg/')
def reg(registration_item: RegistrationObject):
    session_controller.register_user(registration_item.email, registration_item.password, registration_item.phone)


@app.post(ACCESS_TOKEN_USAGE_URL_PART + '/jorm_margin/')
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


@app.get(ACCESS_TOKEN_USAGE_URL_PART + '/jorm_data/')
def upload_data(niche_name: str, _: str = Depends(access_token_correctness_depend)):
    niche: Niche = session_controller.get_niche(niche_name)
    x, y = get_frequency_stats_with_jorm(niche)
    return {'x': x, 'y': y}


@app.get(ACCESS_TOKEN_USAGE_URL_PART + '/save_request/')
def save_request_to_history(request_json: str,
                            access_token: str = Depends(access_token_correctness_depend)):
    user: User = session_controller.get_user(access_token)
    session_controller.save_request(request_json, user)


if __name__ == '__main__':
    uvicorn.run(app, port=8090)
