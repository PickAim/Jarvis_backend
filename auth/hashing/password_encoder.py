from abc import ABC, abstractmethod


class PasswordEncoder(ABC):
    @abstractmethod
    def encode(self, password: str) -> str:
        pass

    @abstractmethod
    def verify(self, password: str, hash: str) -> bool:
        pass
