from pydantic import BaseModel
from jarvis_calc.factories import FactoryKeywords


class MarginJormItem(BaseModel):
    buy: int
    pack: int
    niche: str
    transit_count: int = 0
    transit_price: int = 0
    market_place_transit_price: int = 0
    warehouse_name: str = FactoryKeywords.DEFAULT_WAREHOUSE
