from pydantic import BaseModel


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
