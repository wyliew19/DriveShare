from dataclasses import dataclass, asdict
from fastapi import Form

@dataclass
class FilterSettings:
    """Filter settings for listings
    Dataclass for filtering listings"""
    make: str = Form(None)
    model: str = Form(None)
    year: int = Form(None)
    color: str = Form(None)
    type: str = Form(None)
    price: float = Form(None)
    state: str = Form(None)
    city: str = Form(None)
    start_date: str = Form(None)
    end_date: str = Form(None)

@dataclass
class ListingPost:
    make: str = Form(...)
    model: str = Form(...)
    year: int = Form(...)
    color: str = Form(...)
    car_type: str = Form(...)
    price: float = Form(...)
    city: str = Form(...)
    state: str = Form(...)
    start_date: str = Form(...)
    end_date: str = Form(...)

@dataclass
class SecurityQuestionForm:
    security_answer1: str = Form(...)
    security_answer2: str = Form(...)
    security_answer3: str = Form(...)

def as_dict(dataclass_instance) -> dict[str, str]:
    return asdict(dataclass_instance)