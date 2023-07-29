from abc import ABC
from abc import abstractmethod
from typing import Any


class TokenEncoder(ABC):
    @abstractmethod
    def encode_token(self, payload: dict[str, Any]) -> str:
        pass


class TokenDecoder(ABC):
    @abstractmethod
    def decode_payload(self, token: str) -> dict[str, Any]:
        pass
