from fastapi import Body
from pydantic import BaseModel

from jarvis_backend.controllers.cookie import CookieHandler


class ImprintTokenObject(object):
    def __init__(self, imprint_token: str = Body(None)):
        self.imprint_token = imprint_token


class CookieImprintTokenObject(object):
    def __init__(self, cookie_imprint_token: str = CookieHandler.load_imprint_token()):
        self.cookie_imprint_token = cookie_imprint_token


class AccessTokenObject(object):
    def __init__(self, access_token: str = Body(None), imprint_token: str = Body(None)):
        self.access_token: str = access_token
        self.imprint_token = imprint_token


class CookieAccessTokenObject(object):
    def __init__(self,
                 cookie_access_token: str = CookieHandler.load_access_token(),
                 cookie_imprint_token: str = CookieHandler.load_imprint_token()):
        self.cookie_access_token: str = cookie_access_token
        self.cookie_imprint_token = cookie_imprint_token


class UpdateTokenObject(object):
    def __init__(self, update_token: str = Body(None), imprint_token: str = Body(None)):
        self.update_token: str = update_token
        self.imprint_token = imprint_token


class CookieUpdateTokenObject(object):
    def __init__(self,
                 cookie_update_token: str = CookieHandler.load_update_token(),
                 cookie_imprint_token: str = CookieHandler.load_imprint_token()):
        self.cookie_update_token: str = cookie_update_token
        self.cookie_imprint_token = cookie_imprint_token


class RequestInfoModel(BaseModel):
    name: str
    id: int | None = -1
    timestamp: float = 0.0


class BasicDeleteRequestModel(BaseModel):
    request_id: int


class BasicMarketplaceInfoModel(BaseModel):
    marketplace_id: int


class NicheRequest(BasicMarketplaceInfoModel):
    niche_id: int
    category_id: int


class SimpleEconomyRequestModel(NicheRequest):
    product_exist_cost: int  # user defined cost for product
    cost_price: int  # how much it cost for user
    length: int
    width: int
    height: int
    mass: int
    target_warehouse_name: str


class TransitEconomyRequestModel(SimpleEconomyRequestModel):
    transit_price: int
    transit_count: int


class SimpleEconomyResultModel(BaseModel):
    result_cost: int  # recommended or user defined cost
    logistic_price: int
    storage_price: int
    purchase_cost: int  # cost price OR cost price + transit/count
    marketplace_expanses: int
    absolute_margin: int
    relative_margin: float
    roi: float


class SimpleEconomySaveModel(BaseModel):
    user_result: tuple[SimpleEconomyRequestModel, SimpleEconomyResultModel]
    recommended_result: tuple[SimpleEconomyRequestModel, SimpleEconomyResultModel]
    info: RequestInfoModel = RequestInfoModel.model_validate({'name': "", 'id': None, 'timestamp': 0.0})


class TransitEconomyResult(SimpleEconomyResultModel):
    purchase_investments: int
    commercial_expanses: int
    tax_expanses: int
    absolute_transit_margin: int
    relative_transit_margin: float
    transit_roi: float


class TransitEconomySaveModel(BaseModel):
    user_result: tuple[TransitEconomyRequestModel, TransitEconomyResult]
    recommended_result: tuple[TransitEconomyRequestModel, TransitEconomyResult]
    info: RequestInfoModel = RequestInfoModel.model_validate({'name': "", 'id': None, 'timestamp': 0.0})


class GreenTradeZoneCalculateResultModel(BaseModel):
    segments: list[tuple[int, int]]
    best_segment_idx: int

    segment_profits: list[int]
    best_segment_profit_idx: int

    mean_segment_profit: list[int]
    best_mean_segment_profit_idx: int

    mean_product_profit: list[int]
    best_mean_product_profit_idx: int

    segment_product_count: list[int]
    best_segment_product_count_idx: int

    segment_product_with_trades_count: list[int]
    best_segment_product_with_trades_count_idx: int


class BasicProductRequestModel(BaseModel):
    product_ids: list[int] = []


class ProductRequestModelWithMarketplaceId(BasicProductRequestModel, BasicMarketplaceInfoModel):
    pass


class ProductDownturnResultModel(BaseModel):
    result_dict: dict[int, dict[int, dict[str, int]]]


class ProductTurnoverResultModel(BaseModel):
    result_dict: dict[int, dict[int, dict[str, float]]]


class AllProductCalculateResultObject(BaseModel):
    downturn: ProductDownturnResultModel
    turnover: ProductTurnoverResultModel


class NicheCharacteristicsResultModel(BaseModel):
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


class RegistrationModel(BaseModel):
    email: str = ""
    password: str
    phone: str = ""


class AuthenticationModel(BaseModel):
    login: str = ""
    password: str


class InfoGettingModel(BaseModel):
    is_allow_defaults: bool = False


class GetAllMarketplacesModel(InfoGettingModel):
    pass


class GetAllCategoriesModel(InfoGettingModel, BasicMarketplaceInfoModel):
    pass


class GetAllNichesModel(InfoGettingModel):
    category_id: int


class GetAllProductsModel(BasicMarketplaceInfoModel):
    pass


class AddApiKeyModel(BasicMarketplaceInfoModel):
    api_key: str
