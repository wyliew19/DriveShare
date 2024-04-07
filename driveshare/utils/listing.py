from driveshare.utils.database import DatabaseHandler
from driveshare.models.listing import Listing, Car, Location, Availability

class ListingBuilder:
    """Builds a car listing from user"""
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.listing = Listing()

    def build_listing(self, seller_id: int, buyer_id: int, make: str, model: str, year: int,
                      color: str, car_type: str, price: float, city: str, state: str,
                      days: str, id: int | None = None) -> Listing:
        """Build a car listing"""
        if id is not None:
            self.set_id(id)
        self.set_seller_id(seller_id)
        if buyer_id is not None:
            self.set_buyer_id(buyer_id)
        self.set_car(make, model, year, color, car_type, price)
        self.set_location(city, state)
        self.set_availability(days)
        return self.get_listing()
    
    def set_id(self, id) -> None:
        """Set the id for the listing"""
        self.listing.id = id

    def set_seller_id(self, seller_id) -> None:
        """Set the seller id for the listing"""
        self.listing.seller_id = seller_id
        
    def set_buyer_id(self, buyer_id) -> None:
        """Set the buyer id for the listing"""
        self.listing.buyer_id = buyer_id
    
    def set_car(self, make, model, year, color, car_type, price, location) -> None:
        """Set the car details for the listing"""
        self.listing.car = Car(make, model, year, color, car_type, price, location)

    def set_location(self, city, state) -> None:
        """Set the location for the listing"""
        self.listing.location = Location(city, state)

    def set_availability(self, days) -> None:
        """Set the availability for the listing"""
        self.listing.availability = Availability(days)

    def get_listing(self) -> Listing:
        """Return the car listing"""
        temp = self.listing
        self.reset()
        return temp
        

class ListingMediator:
    """Class to manage car listing operations with database"""

    def _tuple_to_listing(self, listing_tuple: tuple) -> Listing:
        """Convert a tuple from the database to a Listing object"""
        return self.builder.build_listing(listing_tuple[1], listing_tuple[2], listing_tuple[3], listing_tuple[4],
                                          listing_tuple[5], listing_tuple[6], listing_tuple[7], listing_tuple[8],
                                          listing_tuple[10], listing_tuple[11], listing_tuple[12], id=listing_tuple[0])


    def __init__(self):
        self.db = DatabaseHandler()
        self.builder = ListingBuilder()

    def __getitem__(self, id):
        return self.get_listing(id)

    def create_listing(self, email: str, make: str, model: str, year: str,
                       color: str, car_type: str, price: float, city: str, state: str,
                       days: str) -> Listing:
        """Create a new car listing"""

       
        # Get the seller id from the email
        seller_id = self.db.get_user_id(email)
        if seller_id is None:
            raise ValueError("User not found")
        listing = self.builder.build_listing(seller_id, None, make, model, year, color, car_type, price, city, state, days)

        # Save the listing to the database
        self.db.save_listing(listing)
        return listing

    def get_listings(self, id: int | None = None, filters: dict[str, str] | None = None) -> list[Listing]:
        """Get all car listings"""
        listings = self.db.get_listings(id=id, filters=filters)
        ret_list = []
        for listing in listings:
            ret_list.append(self._tuple_to_listing(listing))
        return ret_list

    def get_listing(self, listing_id) -> Listing:
        """Get a specific listing based on id"""
        return self._tuple_to_listing(self.db.get_listing(listing_id))

    def purchase_listing(self, listing_id, buyer_id):
        self.db.purchase_listing(listing_id, buyer_id)
        return (self.get_listing(listing_id).buyer_id == buyer_id)
    