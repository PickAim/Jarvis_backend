import datetime

from jarvis_factory.factories.jorm import FactoryKeywords
from pydantic import BaseModel

DEFAULT_TOKEN_VALUE = "default_token"


class RequestInfo(BaseModel):
    id: int = -1
    date: datetime.datetime = datetime.datetime.utcnow()
    name: str = ""


class UnitEconomyRequestObject(BaseModel):
    buy: int
    pack: int
    niche: str
    transit_count: int = 0
    transit_price: int = 0
    market_place_transit_price: int = 0
    warehouse_name: str = FactoryKeywords.DEFAULT_WAREHOUSE


class UnitEconomyResultObject(BaseModel):
    product_cost: tuple[int, float]  # Закупочная себестоимость
    pack_cost: tuple[int, float]  # Упаковка
    marketplace_commission: tuple[int, float]  # Комиссия маркетплейса
    logistic_price: tuple[int, float]  # Логистика
    storage_price: tuple[int, float]  # Хранение
    margin: tuple[int, float]  # Маржа в копейках
    recommended_price: int
    transit_profit: tuple[int, float]  # Чистая прибыль с транзита
    roi: tuple[float, float]  # ROI
    transit_margin: tuple[float, float]  # Маржа с транзита (%)


class UnitEconomySaveObject(BaseModel):
    request: UnitEconomyRequestObject
    result: UnitEconomyResultObject
    info: RequestInfo


class AuthenticationObject(BaseModel):
    email: str = ""
    password: str
    phone: str = ""
