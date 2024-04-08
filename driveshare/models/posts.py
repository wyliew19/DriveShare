from dataclasses import dataclass, asdict
from fastapi import Form

@dataclass
class FilterSettings:
    """Filter settings for listings
    Dataclass for filtering listings"""
    make: str = Form(...)
    model: str = Form(...)
    year: int = Form(...)
    color: str = Form(...)
    car_type: str = Form(...)
    price: float = Form(...)
    state: str = Form(...)
    city: str = Form(...)
    start_date: str = Form(...)
    end_date: str = Form(...)

@dataclass
class ListingPost:
    email: str = Form(...)
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
    dict_instance = asdict(dataclass_instance)
    for key, value in dict_instance.items():
        if value is None:
            del dict_instance[key]
        dict_instance[key] = str(value)
    return dict_instance