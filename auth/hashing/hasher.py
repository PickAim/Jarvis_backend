from dataclasses import dataclass

from passlib.context import CryptContext

from auth.hashing.passlib_encoder import PasslibEncoder
from auth.tokens.token_control import TokenController


@dataclass
class PasswordHasher:
    def __init__(self, crypt_context: CryptContext):
        self.__password_encoder = PasslibEncoder(crypt_context)
        self.__HASH_KEY: str = 'hash'
        self.__tokenizer: TokenController = TokenController()

    def hash(self, input_sequence: str) -> str:
        key = self.__password_encoder.encode(input_sequence)
        data_to_save = {
            self.__HASH_KEY: key,
        }
        return self.__tokenizer.create_basic_token(data_to_save)

    def verify(self, str_to_check: str, hashed_token: str) -> bool:
        encoded_data = self.__tokenizer.decode_data(hashed_token)
        return self.__password_encoder.verify(str_to_check, encoded_data[self.__HASH_KEY])
