from passlib.context import CryptContext

from jarvis_backend.auth.hashing.password_encoder import PasswordEncoder


class PasslibEncoder(PasswordEncoder):
    def __init__(self, context: CryptContext):
        self.__context = context

    def encode(self, password: str) -> str:
        return self.__context.hash(password)

    def verify(self, password: str, hash_code: str) -> bool:
        return self.__context.verify(password, hash_code)
