import time
import unittest
from dataclasses import dataclass

from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from jarvis_backend.auth.hashing.hasher import PasswordHasher
from jarvis_backend.auth.hashing.passlib_encoder import PasslibEncoder
from jarvis_backend.sessions.exceptions import JarvisExceptionsCode
from jarvis_backend.support.decorators import timeout
from jarvis_backend.support.utils import pydantic_to_jorm, jorm_to_pydantic
from tests.basic import BasicServerTest


@dataclass
class InnerData:
    data: str


@dataclass
class Data:
    inner: InnerData


class InnerDataModel(BaseModel):
    data: str


class DataModel(BaseModel):
    inner: InnerDataModel


class UtilsTest(BasicServerTest):

    def test_pydantic_to_jorm(self):
        to_compare = {
            "inner": {
                "data": "my_data"
            }
        }

        data_model = DataModel.model_validate(to_compare)
        converted = pydantic_to_jorm(Data, data_model)
        self.assertEqual(data_model.inner.data, converted.inner.data)

    def test_jorm_to_pydantic(self):
        data = Data(InnerData("my_data"))
        converted = jorm_to_pydantic(data, DataModel)
        self.assertEqual(data.inner.data, converted.inner.data)

    def test_hasher_verify(self):
        password: str = "password"
        context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        hasher: PasswordHasher = PasswordHasher(context)
        hashed: str = hasher.hash(password)
        self.assertTrue(hasher.verify(password, hashed))

    def test_passlib_encoder(self):
        context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        encoder = PasslibEncoder(context)
        password = "mypAss"
        hash_code = encoder.encode(password)
        self.assertTrue(encoder.verify(password, hash_code))

    def test_timeout_correctness(self):
        @timeout(0.15)
        def timeout_func(a, b):
            time.sleep(0.2)
            return a + b

        with self.assertRaises(HTTPException) as catcher:
            timeout_func(1, 2)
            self.assertJarvisExceptionWithCode(JarvisExceptionsCode.TIMEOUT, catcher.exception)

    def test_not_timeout_correctness(self):
        @timeout()
        def timeout_func(a, b):
            time.sleep(0.2)
            return a + b

        result = timeout_func(1, 2)
        self.assertEqual(3, result)


if __name__ == '__main__':
    unittest.main()
