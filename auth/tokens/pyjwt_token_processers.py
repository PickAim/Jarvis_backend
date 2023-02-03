import jwt
from typing import Any
from auth.tokens.token_processers import (
    TokenDecoder,
    TokenEncoder
)


class PyJwtTokenEncoder(TokenEncoder):
    def __init__(self, key: str, algorithm: str):
        self.__key = key
        self.__algorithm = algorithm

    def provide_token(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, self.__key, self.__algorithm)


class PyJwtTokenDecoder(TokenDecoder):
    def __init__(self, key: str, algorithms: list[str]):
        self.__key = key
        self.__algorithms = algorithms

    def extract_payload(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.__key, self.__algorithms)
