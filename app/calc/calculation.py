from datetime import datetime

from jarvis_calc.calculators.economy_analyze import UnitEconomyCalculator, UnitEconomyCalculateData
from jarvis_calc.calculators.niche_analyze import NicheHistCalculator
from jarvis_calc.calculators.product_analyze import DownturnCalculator
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User

from sessions.request_items import UnitEconomyResultObject, UnitEconomyRequestObject


class CalculationController:
    @staticmethod
    def calc_frequencies(niche: Niche) -> tuple[list[int], list[int]]:
        return NicheHistCalculator.calculate(niche)

    @staticmethod
    def calc_unit_economy(data: UnitEconomyRequestObject,
                          niche: Niche,
                          warehouse: Warehouse,
                          user: User) -> UnitEconomyResultObject:
        return UnitEconomyResultObject.parse_obj(
            UnitEconomyCalculator.calculate(
                UnitEconomyCalculateData(
                    buy_price=data.buy,
                    pack_price=data.pack,
                    transit_price=data.transit_price,
                    transit_count=data.transit_count,
                    market_place_transit_price=data.market_place_transit_price,
                ), niche, warehouse, user
            )
        )

    @staticmethod
    def calc_downturn_days(product: Product, from_date: datetime):
        return DownturnCalculator.calculate(product, from_date)
