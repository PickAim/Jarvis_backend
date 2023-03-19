import random
import string
from datetime import timedelta, datetime

from jorm.server.token.types import TokenType

from auth.tokens import PyJwtTokenEncoder, PyJwtTokenDecoder

letters = string.printable


# "3ARtLTXRn9urnRK9d6rzDbj5Jy5vp/iG8dlaseZliD4="
# TODO split token controller 

class TokenController:
    def __init__(self, key: str = "3ARtLTXRn9urnRK9d6rzDbj5Jy5vp/iG8dlaseZliD4=", algorythm: str = "HS256"):
        self.__algorythm: str = algorythm
        self.__SECRET_KEY = key
        self.__TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
        self.__USER_ID_KEY = "u_id"
        self.__TOKEN_TYPE_KEY = "token_type"
        self.__RND_PART_KEY = "r"
        self.__EXPIRES_TIME_KEY = "exp_time"
        self.__ENCODED_DATA_KEY = "encoded_data"
        self.token_encoder: PyJwtTokenEncoder = PyJwtTokenEncoder(self.__SECRET_KEY, self.__algorythm)
        self.token_decoder: PyJwtTokenDecoder = PyJwtTokenDecoder(self.__SECRET_KEY, [self.__algorythm])

    def create_access_token(self, user_id: int, expires_delta: timedelta = timedelta(minutes=5.0)) -> str:
        return self.__create_session_token(user_id, TokenType.ACCESS, expires_delta, add_random_part=True,
                                           length_of_rand_part=60)

    def create_update_token(self, user_id: int) -> str:
        return self.__create_session_token(user_id, TokenType.UPDATE, add_random_part=True, length_of_rand_part=245)

    def create_imprint_token(self, length_of_rand_part: int = 10) -> str:
        return self.__create_random_part(length_of_rand_part)

    def __create_session_token(self, user_id: int, token_type: TokenType, expires_delta: timedelta = None,
                               add_random_part: bool = False, length_of_rand_part: int = 0) -> str:
        to_encode = {
            self.__USER_ID_KEY: user_id,
            self.__TOKEN_TYPE_KEY: token_type.value
        }
        if expires_delta is not None:
            if expires_delta:
                expires_in = datetime.now() + expires_delta
            else:
                expires_in = datetime.now() + timedelta(minutes=30)
            expires_in = expires_in.replace(microsecond=0)
            to_encode[self.__EXPIRES_TIME_KEY] = str(expires_in)
        return self.create_basic_token(to_encode, add_random_part, length_of_rand_part)

    def create_basic_token(self, to_encode=None, add_random_part: bool = False, length_of_rand_part: int = 0) -> str:
        if add_random_part:
            to_encode[self.__RND_PART_KEY] = self.__create_random_part(length_of_rand_part)
        return self.token_encoder.encode_token(to_encode).decode()

    def decode_data(self, token: str) -> any:
        return self.token_decoder.decode_payload(token.encode())

    def is_token_expired(self, token: str) -> bool:
        decoded_data = self.decode_data(token)
        if self.__EXPIRES_TIME_KEY in decoded_data:
            return datetime.now() > datetime.strptime(decoded_data[self.__EXPIRES_TIME_KEY], self.__TIME_FORMAT)
        return False

    def get_user_id(self, token: str) -> int:
        return int(self.__get_data_by_key(token, self.__USER_ID_KEY))

    def get_token_type(self, token: str) -> int:
        return int(self.__get_data_by_key(token, self.__TOKEN_TYPE_KEY))

    def get_random_part(self, token: str) -> str:
        return str(self.__get_data_by_key(token, self.__RND_PART_KEY))

    def __get_data_by_key(self, token: str, key: str) -> any:
        decoded_data = self.decode_data(token)
        if key in decoded_data:
            return decoded_data[key]
        raise Exception(TokenController.__name__ + ": illegal keyword")

    @staticmethod
    def __create_random_part(length_of_rand_part: int) -> str:
        return ''.join(random.choice(letters) for _ in range(length_of_rand_part))
