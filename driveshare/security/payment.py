from fastapi import HTTPException
from fastapi.responses import RedirectResponse
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

    def authorize(self, password: str, listing: Listing, days: int) -> RedirectResponse:
        db = DatabaseHandler()
        seller_email = db.get_user_email(listing.seller_id)
        amount = listing.car.price * days
        if db.get_balance(self.email) < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        if db.verify_password(self.email, password):
            db.add_balance(seller_email, amount)
            db.purchase_listing(self.email, listing.id, days)
            self.payment.pay(amount)
            return RedirectResponse(url=f"/payment_confirmation$amount={amount:.2f}")
        else:
            raise HTTPException(status_code=401, detail="Invalid password")