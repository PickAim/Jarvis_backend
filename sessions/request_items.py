from jarvis_calc.factories import FactoryKeywords
from pydantic import BaseModel


class RequestObject(BaseModel):
    my_request_type: int = 0
    access_token: str = ""
    update_token: str = ""
    imprint_token: str = ""


class UnitEconomyRequestObject(RequestObject):
    buy: int
    pack: int
    niche: str
    transit_count: int = 0
    transit_price: int = 0
    market_place_transit_price: int = 0
    warehouse_name: str = FactoryKeywords.DEFAULT_WAREHOUSE


class NicheFrequencyObject(RequestObject):
    niche: str


class RequestSaveObject(RequestObject):
    request_json: str


class AuthenticationObject(RequestObject):
    login: str
    password: str


class RegistrationObject(AuthenticationObject):
    phone_number: str
