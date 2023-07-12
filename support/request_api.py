from abc import ABC, abstractmethod
from typing import Callable

from fastapi import APIRouter
from fastapi.types import DecoratedCallable
from jorm.market.person import UserPrivilege, User

from sessions.controllers import JarvisSessionController
from sessions.exceptions import JarvisExceptions, JarvisExceptionsCode


def post(router: APIRouter, path, response_model=None) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return router.post(path, response_model=response_model)


def get(router: APIRouter, path, response_model=None) -> Callable[[DecoratedCallable], DecoratedCallable]:
    return router.get(path, response_model=response_model)


class RequestAPI(ABC):
    @staticmethod
    @abstractmethod
    def _router() -> APIRouter:
        pass

    router = _router()


class RequestAPIWithCheck(RequestAPI, ABC):
    @classmethod
    @abstractmethod
    def get_minimum_privilege(cls) -> UserPrivilege:
        pass

    @classmethod
    def check_and_get_user(cls, session_controller: JarvisSessionController, any_session_token: str) -> User:
        user: User = session_controller.get_user(any_session_token)
        minimum_privilege = cls.get_minimum_privilege()
        current_user_privilege = user.privilege
        if current_user_privilege.value >= minimum_privilege.value:
            return user
        raise JarvisExceptions.create_exception_with_code(
            JarvisExceptionsCode.INCORRECT_GRANT_TYPE,
            "User doesn't have permission to use request"
        )
