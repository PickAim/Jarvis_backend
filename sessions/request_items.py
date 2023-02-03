from jarvis_calc.factories import FactoryKeywords
from pydantic import BaseModel


class BaseRequestObject(BaseModel):
    access_token: str = ""
    update_token: str = ""
    imprint_token: str = ""


class UnitEconomyRequestObject(BaseRequestObject):
    buy: int
    pack: int
    niche: str
    transit_count: int = 0
    transit_price: int = 0
    market_place_transit_price: int = 0
    warehouse_name: str = FactoryKeywords.DEFAULT_WAREHOUSE


class NicheFrequencyObject(BaseRequestObject):
    niche: str


class RequestSaveObject(BaseRequestObject):
    request_json: str


class AuthenticationObject(BaseRequestObject):
    login: str
    password: str


class RegistrationObject(AuthenticationObject):
    phone_number: str
