from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from driveshare.utils.listing import Listing
from driveshare.utils.database import DatabaseHandler
from driveshare.security.hash import Hasher

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
        hasher = Hasher('sha256')
        password_hash = db.get_user_password(self.email)
        email = db.get_user_email(listing.seller_id)
        amount = listing.car.price * days
        if hasher.verify(password, password_hash):
            self.payment.pay(amount)
            return RedirectResponse(url=f"/payment_confirmation$amount={amount:.2f}")
        else:
            raise HTTPException(status_code=401, detail="Invalid password")