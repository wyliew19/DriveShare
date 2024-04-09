from fastapi import HTTPException
from driveshare.utils.listing import Listing
from driveshare.utils.database import DatabaseHandler

class Payment:
    def __init__(self, email: str):
        self.email = email
    
    def pay(self, amount: float):
        print(f"Payment of ${amount:.2f} made by {self.email}")

class PaymentProxy:
    def __init__(self, email: str):
        self.email = email
        self.payment = Payment(email)

    def authorize(self, password: str, listing: Listing, days: int) -> float:
        db = DatabaseHandler()
        seller_email = db.get_user_email(listing.seller_id)
        amount = listing.car.price * days
        if db.verify_password(self.email, password):
            self.payment.pay(amount)
            return amount
        else:
            raise HTTPException(status_code=401, detail="Invalid password")