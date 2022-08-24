from pydantic import BaseModel


class MarginItem(BaseModel):
    buy: float
    pack: float
    units: float
    transit: float
    niche: str
