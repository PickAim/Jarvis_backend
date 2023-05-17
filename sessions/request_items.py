from pydantic import BaseModel


class RequestInfo(BaseModel):
    name: str
    id: int = None
    timestamp: float = 0.0


class UnitEconomyRequestObject(BaseModel):
    buy: int
    pack: int
    niche: str
    transit_count: int = -1
    transit_price: int = -1  # from China to me
    market_place_transit_price: int = -1  # from me to customer
    warehouse_name: str = ""
    marketplace_id: int = 0


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


class RegistrationObject(BaseModel):
    email: str = ""
    password: str
    phone: str = ""


class AuthenticationObject(BaseModel):
    login: str = ""
    password: str
