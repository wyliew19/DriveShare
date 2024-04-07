from driveshare.utils.database import DatabaseHandler
from driveshare.models.listing import Listing, Car

class ListingBuilder:
    """Builds a car listing from user"""
    def __init__(self):
        self.reset()
        
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
        

class ListingManager:
    """Class to manage car listing operations"""

    def _tuple_to_listing(self, listing_tuple: tuple) -> Listing:
        """Convert a tuple from the database to a Listing object"""
        self.builder.set_seller_id(listing_tuple[0])
        self.builder.set_buyer_id(listing_tuple[1])
        self.builder.set_car(listing_tuple[3], listing_tuple[4], listing_tuple[5], listing_tuple[6], listing_tuple[7], listing_tuple[8], listing_tuple[9])
        return self.builder.get_listing()


    def __init__(self):
        self.db = DatabaseHandler()
        self.builder = ListingBuilder()

    def __getitem__(self, id):
        return self.get_listing(id)

    def create_listing(self, seller_id, make, model, year, color, car_type, price, location) -> Listing:
        """Create a new car listing"""
        # Set the seller id and car details
        self.builder.set_seller_id(seller_id)
        self.builder.set_car(make, model, year, color, car_type, price, location)
        # Get the listing object from the builder
        listing = self.builder.get_listing()
        # Save the listing to the database
        self.db.save_listing(listing)
        return listing

    def get_listings(self, id: int | None = None) -> list[Listing]:
        """Get all car listings"""
        if id is not None:
            listings = self.db.get_listings(id)
        else:
            listings = self.db.get_listings()
        ret_list = []
        for listing in listings:
            ret_list.append(self._tuple_to_listing(listing))
        return ret_list

    def get_listing(self, listing_id) -> Listing:
        listing = self.db.get_listing(listing_id)
        self.builder.set_seller_id(listing[0])
        if listing[1] is not None:
            self.builder.set_buyer_id(listing[1])
        self.builder.set_car(listing[3], listing[4], listing[5], listing[6], listing[7], listing[8], listing[9])
        return self.builder.get_listing()

    def purchase_listing(self, listing_id, buyer_id):
        self.db.purchase_listing(listing_id, buyer_id)
        return (self.get_listing(listing_id).buyer_id == buyer_id)
    