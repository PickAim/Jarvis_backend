from typing import Any

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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, RequestInfoModel):
            return False
        return (
                self.name == other.name
                and self.id == other.id
                and self.timestamp == other.timestamp
        )


class BasicDeleteRequestModel(BaseModel):
    request_id: int


class BasicMarketplaceInfoModel(BaseModel):
    marketplace_id: int

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, BasicMarketplaceInfoModel):
            return False
        return self.marketplace_id == other.marketplace_id


class NicheRequest(BasicMarketplaceInfoModel):
    niche_id: int

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NicheRequest):
            return False
        if not super().__eq__(other):
            return False
        return (
                self.niche_id == other.niche_id
        )


class SimpleEconomyRequestModel(NicheRequest):
    product_exist_cost: int  # user defined cost for product
    cost_price: int  # how much it cost for user
    length: float
    width: float
    height: float
    mass: float
    target_warehouse_id: int

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SimpleEconomyRequestModel):
            return False
        if not super().__eq__(other):
            return False
        return (
                self.product_exist_cost == other.product_exist_cost
                and self.cost_price == other.cost_price
                and self.length == other.length
                and self.width == other.width
                and self.height == other.height
                and self.mass == other.mass
                and self.target_warehouse_id == other.target_warehouse_id
        )


class TransitEconomyRequestModel(SimpleEconomyRequestModel):
    logistic_price: int
    logistic_count: int
    transit_cost_for_cubic_meter: float

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TransitEconomyRequestModel):
            return False
        if not super().__eq__(other):
            return False
        return (
                self.logistic_price == other.logistic_price
                and self.logistic_count == other.logistic_count
                and self.transit_cost_for_cubic_meter == other.transit_cost_for_cubic_meter
        )


class SimpleEconomyResultModel(BaseModel):
    result_cost: int  # recommended or user defined cost
    logistic_price: int
    storage_price: int
    purchase_cost: int  # cost price OR cost price + transit/count
    marketplace_expanses: int
    absolute_margin: int
    relative_margin: float
    roi: float

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SimpleEconomyResultModel):
            return False
        return (
                self.result_cost == other.result_cost
                and self.logistic_price == other.logistic_price
                and self.storage_price == other.storage_price
                and self.purchase_cost == other.purchase_cost
                and self.marketplace_expanses == other.marketplace_expanses
                and self.absolute_margin == other.absolute_margin
                and (abs(self.relative_margin - other.relative_margin) < 0.01)
                and (abs(self.roi - other.roi) < 0.01)
        )


class SimpleEconomySaveModel(BaseModel):
    user_result: tuple[SimpleEconomyRequestModel, SimpleEconomyResultModel]
    recommended_result: tuple[SimpleEconomyRequestModel, SimpleEconomyResultModel]
    info: RequestInfoModel = RequestInfoModel.model_validate({'name': "", 'id': -1, 'timestamp': 0.0})

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SimpleEconomySaveModel):
            return False
        for self_item, other_item in zip(self.user_result, other.user_result):
            if self_item != other_item:
                return False
        for self_item, other_item in zip(self.recommended_result, other.recommended_result):
            if self_item != other_item:
                return False
        return self.info == other.info


class TransitEconomyResultModel(SimpleEconomyResultModel):
    purchase_investments: int
    commercial_expanses: int
    tax_expanses: int
    absolute_transit_margin: int
    relative_transit_margin: float
    transit_roi: float

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, TransitEconomyResultModel):
            return False
        if not super().__eq__(other):
            return False
        return (
                self.purchase_investments == other.purchase_investments
                and self.commercial_expanses == other.commercial_expanses
                and self.tax_expanses == other.tax_expanses
                and self.absolute_transit_margin == other.absolute_transit_margin
                and (abs(self.relative_transit_margin - other.relative_transit_margin) < 0.01)
                and (abs(self.transit_roi - other.transit_roi) < 0.01)
        )


class TransitEconomySaveModel(BaseModel):
    user_result: tuple[TransitEconomyRequestModel, TransitEconomyResultModel]
    recommended_result: tuple[TransitEconomyRequestModel, TransitEconomyResultModel]
    info: RequestInfoModel = RequestInfoModel.model_validate({'name': "", 'id': None, 'timestamp': 0.0})

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SimpleEconomySaveModel):
            return False
        for self_item, other_item in zip(self.user_result, other.user_result):
            if self_item != other_item:
                return False
        for self_item, other_item in zip(self.recommended_result, other.recommended_result):
            if self_item != other_item:
                return False
        return self.info == other.info


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


class DownturnInfoModel(BaseModel):
    leftover: int
    days: int


class SingleDownturnResult(BaseModel):
    downturn_info: dict[int, dict[str, DownturnInfoModel]]


class ProductDownturnResultModel(BaseModel):
    result_dict: dict[int, SingleDownturnResult]


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


class GetAllWarehouseModel(InfoGettingModel, BasicMarketplaceInfoModel):
    pass


class AddApiKeyModel(BasicMarketplaceInfoModel):
    api_key: str
