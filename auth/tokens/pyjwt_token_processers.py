from typing import Any

import jwt

from auth.tokens.token_processers import (
    TokenDecoder,
    TokenEncoder
)


class PyJwtTokenEncoder(TokenEncoder):
    def __init__(self, key: str, algorithm: str):
        self.__key = key
        self.__algorithm = algorithm

    def encode_token(self, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, self.__key, self.__algorithm)


class PyJwtTokenDecoder(TokenDecoder):
    def __init__(self, key: str, algorithms: list[str]):
        self.__key = key
        self.__algorithms = algorithms

    def decode_payload(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, key=self.__key, algorithms=self.__algorithms)
