import dataclasses
import json
from datetime import datetime
from typing import TypeVar, Type, Callable

from dacite import from_dict
from jorm.market.items import Product
from jorm.market.service import RequestInfo as JRequestInfo
from jorm.support.utils import intersection
from pydantic import BaseModel

from jarvis_backend.controllers.session import JarvisSessionController
from jarvis_backend.sessions.request_items import RequestInfoModel, ProductRequestModelWithMarketplaceId

T = TypeVar("T")


def pydantic_to_jorm(data_class: Type[T], base_model_object: BaseModel) -> T:
    return from_dict(data_class, json.loads(base_model_object.model_dump_json()))


def jorm_to_pydantic(obj, base_model_class: Type[T]) -> T:
    copy = dataclasses.replace(obj)
    object_dict = _get_object_as_dict(copy)
    return base_model_class.model_validate(object_dict)


def _get_object_as_dict(obj: any) -> dict | str:
    try:
        return json.dumps(obj)
    except Exception:
        return _dump_as_complex_object(obj)


def _tuple_dumps(tuple_obj: tuple) -> tuple:
    return tuple((_get_object_as_dict(item)) for item in tuple_obj)


def _list_dumps(tuple_obj: list) -> list:
    return [(_get_object_as_dict(item)) for item in tuple_obj]


def _datetime_dumps(date: datetime) -> str:
    return json.dumps(date.timestamp())


SPECIAL_DUMPS: dict[Type[T], Callable[[T], any]] = {
    tuple: _tuple_dumps,
    list: _list_dumps,
    datetime: _datetime_dumps
}


def _dump_as_complex_object(obj: any) -> dict | str:
    if type(obj) in SPECIAL_DUMPS:
        return SPECIAL_DUMPS[type(obj)](obj)
    object_dict = obj.__dict__
    for field_name in object_dict:
        field = object_dict[field_name]
        try:
            json.dumps(field)
        except Exception:
            object_dict[field_name] = _get_object_as_dict(field)
    return object_dict


def transform_info(info: RequestInfoModel) -> JRequestInfo:
    if info.timestamp == 0:
        request_time = datetime.utcnow()
    else:
        request_time = datetime.fromtimestamp(info.timestamp)
    return JRequestInfo(info.id, request_time, info.name)


def extract_filtered_user_products_with_history(request_data: ProductRequestModelWithMarketplaceId,
                                                user_id: int, session_controller: JarvisSessionController) \
        -> dict[int, Product]:
    ids_to_filter = request_data.product_ids if request_data is not None else []
    user_products = session_controller.get_products_by_user_atomic(user_id, request_data.marketplace_id)
    filtered_ids = list(user_products.keys())
    if len(ids_to_filter) > 0:
        filtered_ids = intersection(filtered_ids, ids_to_filter)
    return {
        product_id: user_products[product_id]
        for product_id in filtered_ids
    }
