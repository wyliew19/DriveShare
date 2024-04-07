from dataclasses import dataclass

@dataclass
class Car:
    """A car that can be listed"""
    make: str = None
    """Make of the car"""
    model: str = None
    """Model of the car"""
    year: int = None
    """Year of the car"""
    color: str = None
    """Color of the car"""
    car_type: str = None
    """Type of the car"""
    price: float = None
    """Price of the car"""
    location: str = None
    """Location of the rental"""

@dataclass
class Listing:
    """A car listing from user"""
    seller_id: int = None
    """ID of the seller"""
    buyer_id: int = None
    """ID of the buyer"""
    car: Car = None
    """Car details"""