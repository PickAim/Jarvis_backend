from datetime import datetime

from jarvis_calc.calculators.economy_analyze import SimpleEconomyCalculateData, SimpleEconomyCalculator, \
    TransitEconomyCalculateData, TransitEconomyCalculator
from jarvis_calc.calculators.niche_analyze import NicheCharacteristicsCalculator, \
    GreenTradeZoneCalculator
from jarvis_calc.calculators.product_analyze import DownturnCalculator, TurnoverCalculator
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.items import Product
from jorm.market.person import User

from jarvis_backend.sessions.request_items import SimpleEconomyResultModel, SimpleEconomyRequestModel, \
    NicheCharacteristicsResultModel, GreenTradeZoneCalculateResultModel, TransitEconomyRequestModel, \
    TransitEconomyResultModel
from jarvis_backend.support.utils import jorm_to_pydantic


class CalculationController:
    @staticmethod
    def calc_niche_characteristics(niche: Niche) -> NicheCharacteristicsResultModel:
        result = NicheCharacteristicsCalculator.calculate(niche)
        return jorm_to_pydantic(result, NicheCharacteristicsResultModel)

    @staticmethod
    def calc_simple_economy(data: SimpleEconomyRequestModel,
                            niche: Niche,
                            warehouse: Warehouse) -> tuple[SimpleEconomyResultModel, SimpleEconomyResultModel]:
        data = SimpleEconomyCalculateData(
            product_exist_cost=data.product_exist_cost,
            cost_price=data.cost_price,
            length=data.length,
            width=data.width,
            height=data.height,
            mass=data.mass
        )
        result = SimpleEconomyCalculator.calculate(
            data, niche, warehouse
        )
        user_result = jorm_to_pydantic(result[0], SimpleEconomyResultModel)
        recommended_result = jorm_to_pydantic(result[1], SimpleEconomyResultModel)
        return user_result, recommended_result

    @staticmethod
    def calc_transit_economy(data: TransitEconomyRequestModel,
                             user: User,
                             niche: Niche,
                             warehouse: Warehouse) -> tuple[TransitEconomyResultModel, TransitEconomyResultModel]:
        data = TransitEconomyCalculateData(
            product_exist_cost=data.product_exist_cost,
            cost_price=data.cost_price,
            length=data.length,
            width=data.width,
            height=data.height,
            mass=data.mass,
            transit_price=data.transit_price,
            transit_count=data.transit_count
        )
        result = TransitEconomyCalculator.calculate(
            data, niche, user, warehouse
        )
        user_result = jorm_to_pydantic(result[0], TransitEconomyResultModel)
        recommended_result = jorm_to_pydantic(result[1], TransitEconomyResultModel)
        return user_result, recommended_result

    @staticmethod
    def calc_downturn_days(product: Product, from_date: datetime) -> dict[int, dict[str, int]]:
        return DownturnCalculator.calculate(product, from_date)

    @staticmethod
    def calc_turnover(product: Product, from_date: datetime) -> dict[int, dict[str, float]]:
        return TurnoverCalculator.calculate(product, from_date)

    @staticmethod
    def calc_green_zone(niche: Niche, from_date: datetime) -> GreenTradeZoneCalculateResultModel:
        result = GreenTradeZoneCalculator.calculate(niche, from_date)
        return jorm_to_pydantic(result, GreenTradeZoneCalculateResultModel)
