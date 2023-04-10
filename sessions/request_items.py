import datetime

from jorm.support import keywords
from pydantic import BaseModel


class RequestInfo(BaseModel):
    name: str
    id: int = -1
    timestamp: float = datetime.datetime.utcnow().timestamp()


class UnitEconomyRequestObject(BaseModel):
    buy: int
    pack: int
    niche: str
    transit_count: int = -1
    transit_price: int = -1
    market_place_transit_price: int = -1
    warehouse_name: str = keywords.DEFAULT_WAREHOUSE


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
