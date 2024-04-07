from fastapi.responses import RedirectResponse
from driveshare.security.hash import Hasher

class SessionHandler:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance: 
            cls._instance = super(SessionHandler, cls).__new__(cls, *args, **kwargs)
            cls._instance.__init__() 
        return cls._instance

    def __init__(self):
        self.hasher = Hasher('sha256')

    def set_cookie(self, url: str, value: str) -> RedirectResponse:
        response = RedirectResponse(url=url)
        response.set_cookie(key="email", value=self.hasher.hash(value))
        return response

    def confirm_session(self, request) -> bool:
        email = request.cookies.get("email")
        if email:
            return self.hasher.verify(email, email)
        return False