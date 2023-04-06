from jarvis_calc.utils.calculators import FrequencyCalculator, UnitEconomyCalculator
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import Client

from sessions.request_items import UnitEconomyResultObject


class CalculationController:
    def __init__(self):
        self.__frequency_calculator = FrequencyCalculator()
        self.__unit_economy_calculator = UnitEconomyCalculator()

    def calc_frequencies(self, niche: Niche) -> tuple[list[float], list[int]]:
        return self.__frequency_calculator.get_frequency_stats(niche)

    def calc_unit_economy(self, buy_price: int,
                          pack_price: int,
                          niche: Niche,
                          warehouse: Warehouse,
                          client: Client,
                          transit_price: int = 0.0,
                          transit_count: int = 0.0,
                          market_place_transit_price: int = 0.0) -> UnitEconomyResultObject:
        return UnitEconomyResultObject.parse_obj(
            self.__unit_economy_calculator.calc_unit_economy(buy_price, pack_price, niche, warehouse,
                                                             client, transit_price, transit_count,
                                                             market_place_transit_price)
        )
