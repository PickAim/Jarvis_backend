import random
import string
from datetime import timedelta, datetime

from auth.tokens import PyJwtTokenEncoder, PyJwtTokenDecoder

letters = string.printable


# "3ARtLTXRn9urnRK9d6rzDbj5Jy5vp/iG8dlaseZliD4="


class TokenController:
    def __init__(self, key: str, algorythm: str = "HS256"):
        self.__algorythm: str = algorythm
        self.__SECRET_KEY = key
        self.__TIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"
        self.__USER_ID_KEY = "u_id"
        self.__EXPIRES_TIME_KEY = "exp_time"
        self.__ENCODED_DATA_KEY = "encoded_data"
        self.token_encoder: PyJwtTokenEncoder = PyJwtTokenEncoder(self.__SECRET_KEY, self.__algorythm)
        self.token_decoder: PyJwtTokenDecoder = PyJwtTokenDecoder(self.__SECRET_KEY, [self.__algorythm])

    def create_access_token(self, user_id: int, expires_delta: timedelta = timedelta(minutes=5.0)) -> str:
        return self.__create_session_token(user_id, expires_delta, add_random_part=True, length_of_rand_part=60)

    def create_update_token(self, user_id: int) -> str:
        return self.__create_session_token(user_id, add_random_part=True, length_of_rand_part=245)

    def create_imprint_token(self, user_id: int) -> str:
        return self.__create_session_token(user_id, add_random_part=True, length_of_rand_part=5)

    def __create_session_token(self, user_id: int, expires_delta: timedelta = None,
                               add_random_part: bool = False, length_of_rand_part: int = 0) -> str:
        to_encode = {
            self.__USER_ID_KEY: user_id,
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
            to_encode['r'] = ''.join(random.choice(letters) for _ in range(length_of_rand_part))
        return self.token_encoder.encode_token(to_encode)

    def decode_data(self, token: str) -> any:
        return self.token_decoder.decode_payload(token)

    def is_token_expired(self, token: str) -> bool:
        decoded_data = self.decode_data(token)
        if self.__EXPIRES_TIME_KEY in decoded_data:
            return datetime.now() > datetime.strptime(decoded_data[self.__EXPIRES_TIME_KEY], self.__TIME_FORMAT)
        return False

    def get_user_id(self, token: str) -> int:
        decoded_data = self.decode_data(token)
        if self.__USER_ID_KEY in decoded_data:
            return int(decoded_data[self.__USER_ID_KEY])
        return -1
