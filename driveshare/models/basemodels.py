from pydantic import BaseModel
from typing import List

class FilterSettings(BaseModel):
    email: str = None
    make: str = None
    model: str = None
    year: int = None
    color: str = None
    car_type: str = None
    price: float = None
    state: str = None
    city: str = None
    days: str = None

class Search(BaseModel):
    filters: List[FilterSettings]

class ListingPost(BaseModel):
    email: str = None
    make: str = None
    model: str = None
    year: int = None
    color: str = None
    car_type: str = None
    price: float = None
    state: str = None
    city: str = None
    days: str = None