from fastapi import Depends

from jarvis_backend.auth import TokenController
from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.dependencies import session_controller_depend
from jarvis_backend.sessions.exceptions import JarvisExceptions
from jarvis_backend.sessions.request_items import AccessTokenObject, UpdateTokenObject, CookieUpdateTokenObject, \
    CookieAccessTokenObject, ImprintTokenObject, CookieImprintTokenObject


def check_token_correctness(any_session_token: str, imprint_token: str,
                            session_controller: JarvisSessionController) -> str:
    if session_controller.check_token_correctness(any_session_token, imprint_token):
        return any_session_token
    else:
        raise JarvisExceptions.INCORRECT_TOKEN


def imprint_token_correctness_depend(imprint_token_object: ImprintTokenObject = Depends(),
                                     cookie_imprint_token_object: CookieImprintTokenObject = Depends()) -> str | None:
    if imprint_token_object.imprint_token is not None \
            and imprint_token_object.imprint_token != "":
        return imprint_token_object.imprint_token
    elif cookie_imprint_token_object.cookie_imprint_token is not None \
            and cookie_imprint_token_object.cookie_imprint_token:
        return cookie_imprint_token_object.cookie_imprint_token
    else:
        return None


def get_non_empty_token(first_token: str | None, second_token: str | None) -> str:
    if first_token is not None and first_token != "":
        return first_token
    elif second_token is not None and second_token != "":
        return second_token
    raise JarvisExceptions.INCORRECT_TOKEN


def access_token_correctness_post_depend(access_token_object: AccessTokenObject = Depends(),
                                         cookie_access_token_object: CookieAccessTokenObject = Depends(),
                                         session_controller: JarvisSessionController = Depends(
                                             session_controller_depend)) -> str:
    access_token = get_non_empty_token(
        cookie_access_token_object.cookie_access_token,
        access_token_object.access_token
    )
    imprint_token = get_non_empty_token(
        cookie_access_token_object.cookie_imprint_token,
        access_token_object.imprint_token
    )
    if TokenController().is_token_expired(access_token):
        raise JarvisExceptions.EXPIRED_TOKEN
    return check_token_correctness(access_token, imprint_token, session_controller)


def update_token_correctness_post_depend(update_token_object: UpdateTokenObject = Depends(),
                                         cookie_update_token_object: CookieUpdateTokenObject = Depends(),
                                         session_controller: JarvisSessionController = Depends(
                                             session_controller_depend)) -> str:
    access_token = get_non_empty_token(
        cookie_update_token_object.cookie_update_token,
        update_token_object.update_token
    )
    imprint_token = get_non_empty_token(
        cookie_update_token_object.cookie_imprint_token,
        update_token_object.imprint_token
    )
    if TokenController().is_token_expired(access_token):
        raise JarvisExceptions.EXPIRED_TOKEN
    return check_token_correctness(access_token, imprint_token, session_controller)
