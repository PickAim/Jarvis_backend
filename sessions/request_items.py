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
    product_cost: int  # Закупочная себестоимость
    pack_cost: int  # Упаковка
    marketplace_commission: int  # Комиссия маркетплейса
    logistic_price: int  # Логистика
    storage_price: int  # Хранение
    margin: int  # Маржа в копейках
    recommended_price: int
    transit_profit: int  # Чистая прибыль с транзита
    roi: float  # ROI
    transit_margin: float  # Маржа с транзита (%)


class UnitEconomySaveObject(BaseModel):
    request: UnitEconomyRequestObject
    result: UnitEconomyResultObject
    info: RequestInfo


class AuthenticationObject(BaseModel):
    email: str = ""
    password: str
    phone: str = ""
