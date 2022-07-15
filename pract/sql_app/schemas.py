from typing import List, Union
from datetime import datetime

from pydantic import BaseModel


class PriceBase(BaseModel):
    name:str
    url:str=None
    price:str
    price_float:float
    price_for_one:str

class PriceCreate(PriceBase):
    pass

class Price(PriceBase):
    id:int
    datetime:datetime

    class Config:
        orm_mode = True
