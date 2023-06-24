from datetime import datetime

from jarvis_calc.calculators.economy_analyze import UnitEconomyCalculator
from jarvis_calc.calculators.niche_analyze import NicheAnalyzeCalculator
from jarvis_calc.calculators.product_analyze import DownturnCalculator
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User

from sessions.request_items import UnitEconomyResultObject


class CalculationController:
    def __init__(self):
        self.__frequency_calculator = NicheAnalyzeCalculator()
        self.__unit_economy_calculator = UnitEconomyCalculator()
        self.__downturn_calculator = DownturnCalculator()

    def calc_frequencies(self, niche: Niche) -> tuple[list[int], list[int]]:
        return self.__frequency_calculator.calculate_niche_hist(niche)

    def calc_unit_economy(self, buy_price: int,
                          pack_price: int,
                          niche: Niche,
                          warehouse: Warehouse,
                          user: User,
                          transit_price: int = 0.0,
                          transit_count: int = 0.0,
                          market_place_transit_price: int = 0.0) -> UnitEconomyResultObject:
        return UnitEconomyResultObject.parse_obj(
            self.__unit_economy_calculator.calculate(buy_price, pack_price, niche, warehouse,
                                                     user, transit_price, transit_count,
                                                     market_place_transit_price)
        )

    def calc_downturn_days(self, product: Product, from_date: datetime):
        return self.__downturn_calculator.calculate(product, from_date)
