from fastapi import Depends
from jarvis_factory.factories.jcalc import JCalcClassesFactory

from auth import TokenController
from sessions.controllers import CookieHandler, JarvisSessionController
from sessions.dependencies import session_depend
from sessions.exceptions import JarvisExceptions
from sessions.request_handler import RequestHandler, SAVE_METHODS, GET_ALL_METHODS, DELETE_METHODS


def session_controller_depend(session=Depends(session_depend)) -> JarvisSessionController:
    db_controller = JCalcClassesFactory.create_db_controller(session)
    return JarvisSessionController(db_controller)


def request_handler_depend(session=Depends(session_depend)) -> RequestHandler:
    db_controller = JCalcClassesFactory.create_db_controller(session)
    return RequestHandler(db_controller, SAVE_METHODS, GET_ALL_METHODS, DELETE_METHODS)


def check_token_correctness(any_session_token: str, imprint_token: str,
                            session_controller: JarvisSessionController) -> str:
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
                                    imprint_token: str = Depends(imprint_token_correctness_depend),
                                    session_controller: JarvisSessionController = Depends(
                                        session_controller_depend)) -> str:
    token_to_check: str
    if cookie_access_token is not None:
        token_to_check = cookie_access_token
    elif access_token is not None:
        token_to_check = access_token
    else:
        raise JarvisExceptions.INCORRECT_TOKEN

    if TokenController().is_token_expired(token_to_check):
        raise JarvisExceptions.EXPIRED_TOKEN
    return check_token_correctness(token_to_check, imprint_token, session_controller)


def update_token_correctness_depend(update_token: str = None,
                                    cookie_update_token: str = CookieHandler.load_update_token(),
                                    imprint_token: str = Depends(imprint_token_correctness_depend),
                                    session_controller: JarvisSessionController = Depends(
                                        session_controller_depend)) -> str:
    if cookie_update_token is not None:
        return check_token_correctness(cookie_update_token, imprint_token, session_controller)
    elif update_token is not None:
        return check_token_correctness(update_token, imprint_token, session_controller)
    else:
        raise JarvisExceptions.INCORRECT_TOKEN
