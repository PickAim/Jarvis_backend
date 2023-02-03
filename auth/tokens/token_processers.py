from abc import ABC
from abc import abstractmethod
from typing import Any


class TokenEncoder(ABC):
    @abstractmethod
    def provide_token(self, payload: dict[str, Any]) -> str:
        pass


class TokenDecoder(ABC):
    @abstractmethod
    def extract_payload(self, token: str) -> dict[str, Any]:
        pass
