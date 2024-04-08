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
                      start_date: str, end_date: str, id: int | None = None) -> Listing:
        """Build a car listing"""
        if id is not None:
            self.set_id(id)
        self.set_seller_id(seller_id)
        if buyer_id is not None:
            self.set_buyer_id(buyer_id)
        self.set_car(make, model, year, color, car_type, price)
        self.set_location(city, state)
        self.set_availability(start_date, end_date)
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
    
    def set_car(self, make, model, year, color, car_type, price) -> None:
        """Set the car details for the listing"""
        self.listing.car = Car(make, model, year, color, car_type, price)

    def set_location(self, city, state) -> None:
        """Set the location for the listing"""
        self.listing.location = Location(city, state)

    def set_availability(self, start_date, end_date) -> None:
        """Set the availability for the listing"""
        self.listing.availability = Availability(start_date, end_date)

    def get_listing(self) -> Listing:
        """Return the car listing"""
        temp = self.listing
        self.reset()
        return temp
        

class ListingMediator:
    """Class to manage car listing operations with database"""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ListingMediator, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__()
        return cls._instance
    
    def __init__(self):
        self.db = DatabaseHandler()
        self.builder = ListingBuilder()

    def __getitem__(self, id):
        return self.get_listing(id)

    def _tuple_to_listing(self, listing_tuple: tuple) -> Listing:
        """Convert a tuple from the database to a Listing object"""
        return self.builder.build_listing(listing_tuple[1], listing_tuple[2], listing_tuple[3], listing_tuple[4],
                                          listing_tuple[5], listing_tuple[6], listing_tuple[7], listing_tuple[8],
                                          listing_tuple[9], listing_tuple[10], listing_tuple[11], listing_tuple[12],
                                          id=listing_tuple[0])


    def create_listing(self, email: str, make: str, model: str, year: str,
                       color: str, car_type: str, price: float, city: str, state: str,
                       start_date: str, end_date: str) -> Listing:
        """Create a new car listing"""
        # Get the seller id from the email
        seller_id = self.db.get_user_id(email)
        if seller_id is None:
            raise ValueError("User not found")
        listing = self.builder.build_listing(seller_id, None, make, model, year, color, car_type, price, city,
                                             state, start_date, end_date)

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

    def get_purchase_history(self, id: int) -> list[Listing]:
        """Get the purchase history of a user"""
        listings = self.db.get_purchase_history(id)
        ret_list = []
        for listing in listings:
            ret_list.append(self._tuple_to_listing(listing))
        return ret_list
    