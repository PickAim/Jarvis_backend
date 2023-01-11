from pydantic import BaseModel
from jarvis_calc.factories import FactoryKeywords


class MarginItem(BaseModel):
    buy: int
    pack: int
    storage_price: int
    logistic_to_customer: int
    transit_count: int
    transit_price: int
    niche: str
    commission: float
    returned_percent: float
    client_tax: float


class MarginJormItem(BaseModel):
    buy: int
    pack: int
    niche: str
    transit_count: int = 0
    transit_price: int = 0
    warehouse_name: str = FactoryKeywords.DEFAULT_WAREHOUSE

