import json
from datetime import datetime
from typing import TypeVar, Type

from dacite import from_dict
from jorm.market.service import RequestInfo as JRequestInfo, Request, Result
from pydantic import BaseModel

from sessions.request_items import BasicSaveObject, RequestInfo
from support.types import JBasicSaveObject

T = TypeVar("T")


def pydantic_to_jorm(data_class: Type[T], base_model_object: BaseModel) -> T:
    return from_dict(data_class, json.loads(base_model_object.json()))


def jorm_to_pydantic(obj, base_model_class: Type[T]) -> T:
    return base_model_class.parse_obj(obj.__dict__)


def transform_info(info: RequestInfo) -> JRequestInfo:
    if info.timestamp == 0:
        request_time = datetime.utcnow()
    else:
        request_time = datetime.fromtimestamp(info.timestamp)
    return JRequestInfo(info.id, request_time, info.name)


def convert_save_objects_to_jorm(save_object: BasicSaveObject, type_to_convert: Type[JBasicSaveObject]):
    jorm_request: Request = pydantic_to_jorm(type_to_convert.request_type, save_object.request)
    jorm_result: Result = pydantic_to_jorm(type_to_convert.result_type, save_object.result)
    info: JRequestInfo = transform_info(save_object.info)
    return type_to_convert(jorm_request, jorm_result, info)


def convert_save_objects_to_pydantic(type_to_convert: Type[BasicSaveObject], request: Request,
                                     result: Result, info: RequestInfo):
    pydantic_request = jorm_to_pydantic(request, type_to_convert.__annotations__['request'])
    pydantic_result = jorm_to_pydantic(result, type_to_convert.__annotations__['result'])
    pydantic_info = jorm_to_pydantic(info, RequestInfo)
    return type_to_convert.parse_obj(
        {
            'request': pydantic_request,
            'result': pydantic_result,
            'info': pydantic_info
        }
    )
