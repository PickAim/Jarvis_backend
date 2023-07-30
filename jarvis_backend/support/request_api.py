from abc import ABC, abstractmethod

from fastapi import APIRouter
from jorm.market.person import UserPrivilege, User

from jarvis_backend.app.tags import OTHER_TAG
from jarvis_backend.sessions.controllers import JarvisSessionController
from jarvis_backend.sessions.exceptions import JarvisExceptions, JarvisExceptionsCode


class RequestAPI(ABC):
    @staticmethod
    def _router() -> APIRouter:
        return APIRouter(tags=[OTHER_TAG])

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
