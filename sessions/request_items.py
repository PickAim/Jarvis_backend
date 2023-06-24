from pydantic import BaseModel


class RequestInfo(BaseModel):
    name: str
    id: int = None
    timestamp: float = 0.0


class BasicSaveObject(BaseModel):
    request: BaseModel = ""
    result: BaseModel = ""
    info: RequestInfo = RequestInfo.parse_obj({'name': "", 'id': None, 'timestamp': 0.0})


class FrequencyRequest(BaseModel):
    niche_name: str
    category_name: str
    marketplace_id: int


class FrequencyResult(BaseModel):
    frequencies: dict[int, int]


class FrequencySaveObject(BasicSaveObject):
    request: FrequencyRequest
    result: FrequencyResult


class UnitEconomyRequestObject(BaseModel):
    buy: int
    pack: int
    niche: str
    category: str
    marketplace_id: int
    transit_count: int = -1
    transit_price: int = -1  # from China to me
    market_place_transit_price: int = -1  # from me to customer
    warehouse_name: str = ""


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


class UnitEconomySaveObject(BasicSaveObject):
    request: UnitEconomyRequestObject
    result: UnitEconomyResultObject


class ProductDownturnResultObject(BaseModel):
    result_dict: dict[int, dict[int, dict[str, int]]]


class ProductDownturnSaveObject(BasicSaveObject):
    result: ProductDownturnResultObject


class RegistrationObject(BaseModel):
    email: str = ""
    password: str
    phone: str = ""


class AuthenticationObject(BaseModel):
    login: str = ""
    password: str
