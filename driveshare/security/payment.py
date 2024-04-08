from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from driveshare.utils.database import DatabaseHandler
from driveshare.security.hash import Hasher

class PaymentProxy:
    def __init__(self, email: str):
        self.email = email

    def authorize(self, password: str) -> RedirectResponse:
        db = DatabaseHandler()
        hasher = Hasher('sha256')
        password_hash = db.get_user_password(self.email)
        if hasher.verify(password, password_hash):
            return RedirectResponse(url="/payment/")
        else:
            raise HTTPException(status_code=401, detail="Invalid password")