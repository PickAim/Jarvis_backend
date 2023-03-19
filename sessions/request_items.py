from jarvis_factory.factories.jorm import FactoryKeywords
from pydantic import BaseModel

DEFAULT_TOKEN_VALUE = "default_token"


class UnitEconomyRequestObject(BaseModel):
    buy: int
    pack: int
    niche: str
    transit_count: int = 0
    transit_price: int = 0
    market_place_transit_price: int = 0
    warehouse_name: str = FactoryKeywords.DEFAULT_WAREHOUSE


class AuthenticationObject(BaseModel):
    email: str
    password: str
    phone: str = ""
