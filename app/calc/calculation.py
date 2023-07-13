from datetime import datetime

from jarvis_calc.calculators.economy_analyze import UnitEconomyCalculator, UnitEconomyCalculateData
from jarvis_calc.calculators.niche_analyze import NicheHistCalculator
from jarvis_calc.calculators.product_analyze import DownturnCalculator
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User

from sessions.request_items import UnitEconomyResultObject, UnitEconomyRequestObject
from support.utils import jorm_to_pydantic


class CalculationController:
    @staticmethod
    def calc_frequencies(niche: Niche) -> dict[str, list[int]]:
        result = NicheHistCalculator.calculate(niche)
        return {
            'x': result[0],
            'y': result[1]
        }

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
    def calc_downturn_days(product: Product, from_date: datetime):
        return DownturnCalculator.calculate(product, from_date)
