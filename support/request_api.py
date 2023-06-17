from abc import ABC, abstractmethod
from typing import Callable

from fastapi import APIRouter
from fastapi.types import DecoratedCallable


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
