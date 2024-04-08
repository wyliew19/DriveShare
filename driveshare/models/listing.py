from dataclasses import dataclass

@dataclass
class Availability:
    """Availability of the listing"""
    start_date: str = None
    """Start date of availability"""
    end_date: str = None
    """End date of availability"""

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

@dataclass
class Location:
    """Location of the listing"""
    city: str = None
    """City of the listing"""
    state: str = None
    """State of the listing"""

@dataclass
class Listing:
    """A car listing from user"""
    id: int = None
    """ID of the listing"""
    seller_id: int = None
    """ID of the seller"""
    buyer_id: int = None
    """ID of the buyer"""
    car: Car = None
    """Car details"""
    location: Location = None
    """Location of the rental"""
    availability: Availability = None
    """Availability of the car"""