from datetime import datetime

from jarvis_calc.calculators.economy_analyze import UnitEconomyCalculator, UnitEconomyCalculateData
from jarvis_calc.calculators.niche_analyze import NicheCharacteristicsCalculator, \
    GreenTradeZoneCalculator
from jarvis_calc.calculators.product_analyze import DownturnCalculator, TurnoverCalculator
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User

from jarvis_backend.sessions.request_items import UnitEconomyResultObject, UnitEconomyRequestObject, \
    NicheCharacteristicsResultObject, GreenTradeZoneCalculateResultObject
from jarvis_backend.support.utils import jorm_to_pydantic


class CalculationController:
    @staticmethod
    def calc_niche_characteristics(niche: Niche) -> NicheCharacteristicsResultObject:
        result = NicheCharacteristicsCalculator.calculate(niche)
        return jorm_to_pydantic(result, NicheCharacteristicsResultObject)

    @staticmethod
    def calc_unit_economy(data: UnitEconomyRequestObject,
                          niche: Niche,
                          warehouse: Warehouse,
                          user: User) -> UnitEconomyResultObject:
        result = UnitEconomyCalculator.calculate(
            UnitEconomyCalculateData(
                buy_price=data.buy,
                pack_price=data.pack,
                transit_price=data.transit_price,
                transit_count=data.transit_count,
                market_place_transit_price=data.market_place_transit_price,
            ), niche, warehouse, user
        )
        return jorm_to_pydantic(result, UnitEconomyResultObject)

    @staticmethod
    def calc_downturn_days(product: Product, from_date: datetime) -> dict[int, dict[str, int]]:
        return DownturnCalculator.calculate(product, from_date)

    @staticmethod
    def calc_turnover(product: Product, from_date: datetime) -> dict[int, dict[str, float]]:
        return TurnoverCalculator.calculate(product, from_date)

    @staticmethod
    def calc_green_zone(niche: Niche, from_date: datetime) -> GreenTradeZoneCalculateResultObject:
        result = GreenTradeZoneCalculator.calculate(niche, from_date)
        return jorm_to_pydantic(result, GreenTradeZoneCalculateResultObject)
