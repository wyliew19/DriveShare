import sqlite3
from dataclasses import dataclass
from database import DatabaseHandler

@dataclass
class Car:
    """A car that can be listed"""
    make: str = None
    model: str = None
    year: int = None
    color: str = None
    car_type: str = None 
    price: float = None
    location: str = None

@dataclass
class Listing:
    """A car listing from user"""
    seller_id: int = None
    buyer_id: int = None
    car: Car = None

class ListingBuilder:
    """Builds a car listing from user"""
    def __init__(self, database_name='driveshare.db'):
        self.db = DatabaseHandler(database_name)
        
    def reset(self):
        self.listing = Listing()

    def set_seller_id(self, seller_id) -> None:
        """Set the seller id for the listing"""
        self.listing.seller_id = seller_id
        
    def set_buyer_id(self, buyer_id) -> None:
        """Set the buyer id for the listing"""
        self.listing.buyer_id = buyer_id
    
    def set_car(self, make, model, year, color, car_type, price, location) -> None:
        """Set the car details for the listing"""
        self.listing.car = Car(make, model, year, color, car_type, price, location)

    def get_listing(self) -> Listing:
        """Return the car listing"""
        temp = self.listing
        self.reset()
        return temp

    def save(self) -> Listing:
        """Save the car listing to the database and reset the builder"""
        self.db.save_listing(self.listing)
        return self.get_listing()
        

class ListingManager:

    def __init__(self, database_name='driveshare.db'):
        self.db = DatabaseHandler(database_name)
        self.builder = ListingBuilder(self.db)

    def create_listing(self, seller_id, make, model, year, color, car_type, price, location):
        self.builder.set_seller_id(seller_id)
        self.builder.set_car(make, model, year, color, car_type, price, location)
        return self.builder.save()

    def get_listings(self) -> list[Listing]:
        listings = self.db.get_listings()
        ret_list = []
        for listing in listings:
            self.builder.set_seller_id(listing[0])
            if listing[1] is not None:
                self.builder.set_buyer_id(listing[1])
            self.builder.set_car(listing[3], listing[4], listing[5], listing[6], listing[7], listing[8], listing[9])
            ret_list.append(self.builder.get_listing())
        return ret_list

    def get_listing(self, listing_id) -> Listing:
        listing = self.db.get_listing(listing_id)
        self.builder.set_seller_id(listing[0])
        if listing[1] is not None:
            self.builder.set_buyer_id(listing[1])
        self.builder.set_car(listing[3], listing[4], listing[5], listing[6], listing[7], listing[8], listing[9])
        return self.builder.get_listing()


    