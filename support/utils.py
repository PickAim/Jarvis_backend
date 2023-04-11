import json
from typing import TypeVar, Type

from dacite import from_dict
from pydantic import BaseModel

T = TypeVar("T")


def pydantic_to_jorm(data_class: Type[T], base_model_object: BaseModel) -> T:
    return from_dict(data_class, json.loads(base_model_object.json()))


def jorm_to_pydantic(obj, base_model_class: Type[T]) -> T:
    return base_model_class.parse_obj(obj.__dict__)
