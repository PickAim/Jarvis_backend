from pydantic import BaseModel


class MarginItem(BaseModel):
    buy: int
    pack: int
    units: int
    transit: int
    niche: str
