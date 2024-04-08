from fastapi import HTTPException, Depends
from driveshare.security.cookie import OAuth2WithCookie
from driveshare.utils.user import UserMediator
from driveshare.utils.listing import ListingMediator
from driveshare.models.user import User

from typing import Annotated

oauth2_scheme = OAuth2WithCookie(tokenUrl="/token")

def get_current_user(email: Annotated[str, Depends(oauth2_scheme)]) -> User:
    user_manager = UserMediator()
    user = user_manager[email]
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

def get_user_manager():
    return UserMediator()

def get_listing_manager():
    return ListingMediator()