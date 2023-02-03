import base64
import hashlib
import os
from dataclasses import dataclass

from auth.tokens.token_control import TokenController


@dataclass
class Hasher:
    def __init__(self):
        self.__HASH_KEY: str = 'hash'
        self.__SALT_KEY: str = 'salt'
        self.__IT_NUM_KEY: str = 'it_num'
        self.__DKLEN_KEY: str = 'dklen'
        self.__tokenizer: TokenController = TokenController()

    def hash(self, input_sequence: str, salt: bytes = os.urandom(32),
             iteration_num: int = 123456, dklen: int = 128) -> str:
        key = hashlib.pbkdf2_hmac('sha256', input_sequence.encode('utf-8'), salt, iteration_num, dklen=dklen)
        data_to_save = {
            self.__HASH_KEY: base64.b64encode(key).decode('ascii'),
            self.__SALT_KEY: base64.b64encode(salt).decode('ascii'),
            self.__IT_NUM_KEY: iteration_num,
            self.__DKLEN_KEY: dklen
        }
        return self.__tokenizer.create_basic_token(data_to_save)

    def verify(self, str_to_check: str, hashed_token: str) -> bool:
        encoded_data = self.__tokenizer.decode_data(hashed_token)
        salt: bytes = base64.standard_b64decode(encoded_data[self.__SALT_KEY])
        iteration_num: int = encoded_data[self.__IT_NUM_KEY]
        dklen: int = encoded_data[self.__DKLEN_KEY]
        to_check = self.__tokenizer.decode_data(self.hash(str_to_check, salt, iteration_num, dklen))
        return to_check[self.__HASH_KEY] == encoded_data[self.__HASH_KEY]
