from pydantic import BaseModel


class RequestInfo(BaseModel):
    name: str
    id: int | None = -1
    timestamp: float = 0.0


class BasicSaveObject(BaseModel):
    request: BaseModel = ""
    result: BaseModel = ""
    info: RequestInfo = RequestInfo.model_validate({'name': "", 'id': None, 'timestamp': 0.0})


class NicheRequest(BaseModel):
    niche: str
    category_id: int
    marketplace_id: int


class FrequencyRequest(NicheRequest):
    pass


class FrequencyResult(BaseModel):
    x: list[int]
    y: list[int]


class FrequencySaveObject(BasicSaveObject):
    request: FrequencyRequest
    result: FrequencyResult


class UnitEconomyRequestObject(NicheRequest):
    buy: int
    pack: int
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


class ProductTurnoverResultObject(BaseModel):
    result_dict: dict[int, dict[int, dict[str, float]]]


class NicheCharacteristicsResultObject(BaseModel):
    card_count: int
    niche_profit: int
    card_trade_count: int
    mean_card_rating: float
    card_with_trades_count: int
    daily_mean_niche_profit: int
    daily_mean_trade_count: int
    mean_traded_card_cost: int
    month_mean_niche_profit_per_card: int
    monopoly_percent: float
    maximum_profit_idx: int


class RegistrationObject(BaseModel):
    email: str = ""
    password: str
    phone: str = ""


class AuthenticationObject(BaseModel):
    login: str = ""
    password: str