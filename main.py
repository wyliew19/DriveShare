from typing import Annotated
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from driveshare.utils.user import UserMediator
from driveshare.utils.listing import ListingMediator
from driveshare.models.posts import ListingPost, FilterSettings, as_dict
from driveshare.models.user import User
from driveshare.security.payment import PaymentProxy
from driveshare.di import get_current_user, get_user_manager, get_listing_manager

# Create a FastAPI instance and mount static files
app = FastAPI()
app.mount("/static", StaticFiles(directory=Path('driveshare/interface').resolve()), name="static")
templates = Jinja2Templates(directory="driveshare/interface")

####### Root Page ##################################

@app.get("/", response_class=HTMLResponse)
def registration(request: Request):
    return templates.TemplateResponse("registration.html", {"request": request})

####### Login Page and Authentication ##############

@app.get("/login_page", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], user_manager: Annotated[UserMediator, Depends(get_user_manager)], response: Response):
    user = user_manager.login(form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid username or password", headers={"WWW-Authenticate": "Bearer"})
    response.set_cookie(key="access_token", value=f'bearer {form.username}')
    return {"access_token": form.username, "token_type": "bearer"}
    

@app.get("/home", response_class=HTMLResponse)
def handle_home_page(request: Request, user: Annotated[User, Depends(get_current_user)]):
    print(f'User is {user}')
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

####### Login Page and Authentication ##############

####### Logout #####################################

@app.get("/logout", response_class=RedirectResponse)
def logout():
    response = RedirectResponse(url="/login_page")
    response.delete_cookie("access_token")
    return response

####### Logout #####################################

####### Payment ####################################

@app.get("/payment/auth", response_class=HTMLResponse)
def authorize(request: Request, listing_id: int, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
              user = Depends(get_current_user)):
    listing = listing_manager.get_listing(listing_id)
    strip_date = lambda x: datetime.strptime(x, "%Y-%m-%d")
    start_date = strip_date(listing.availability.start_date)
    end_date = strip_date(listing.availability.end_date)
    max_days = (end_date - start_date).days
    return templates.TemplateResponse("payment.html", {"request": request, "user": user, "max_days": max_days, "listing": listing})

@app.post("/payment/auth")
def payment(password: Annotated[str, Form(...)], days: Annotated[int, Form(...)],
            listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
            listing_id: int, user = Depends(get_current_user)):
    proxy = PaymentProxy(user.email)
    amount = listing_manager.get_listing(listing_id).price * days
    return proxy.authorize(password, amount)

@app.get("/payment_confirmation")
def payment_confirmation(request: Request, amount: str, user = Depends(get_current_user)):
    return templates.TemplateResponse("payment_confirmation.html", {"request": request, "user": user, "amount": amount})

####### Payment ####################################

####### Registration ###############################

@app.post("/register")
def register(form: Annotated[OAuth2PasswordRequestForm, Depends()], user_manager: Annotated[UserMediator, Depends(get_user_manager)], response: Response):
    user = user_manager.register(email=form.username, password=form.password)
    response.set_cookie(key="access_token", value=f'bearer {form.username}')
    if user is None:
        raise HTTPException(status_code=409, detail="User already exists")
    return {"access_token": form.username, "token_type": "bearer"}
    

@app.get("/register_confirmation", response_class=HTMLResponse)
def handle_registration_confirmation(request: Request):
    return templates.TemplateResponse("registration_confirmation.html", {"request": request})

####### Registration ################################

####### Listings #####################################

@app.get("/listings", response_class=HTMLResponse)
def listings(request: Request, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    listings = listing_manager.get_listings()
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings})

@app.post("/listings", response_class=HTMLResponse)
def filter_listings(request: Request, filters: Annotated[FilterSettings, Depends()], listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    filters = as_dict(filters)
    listings = listing_manager.get_listings(filters=filters)
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings})

@app.get("/listings/{id}", response_class=HTMLResponse)
def listing(request: Request, id: int, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    listing = listing_manager.get_listing(id)
    return templates.TemplateResponse("listing.html", {"request": request, "listing": listing})

@app.get("/my_listings", response_class=HTMLResponse)
def my_listings(request: Request, user: Annotated[User, Depends(get_current_user)], listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    listings = listing_manager.get_listings(user.id)
    return templates.TemplateResponse("my_listings.html", {"request": request, "listings": listings})

@app.get("/listings/post", response_class=HTMLResponse)
def post_listing(request: Request):
    return templates.TemplateResponse("post_listing.html", {"request": request})

@app.post("/listings/post")
def post_listing(request: Request, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    post = ListingPost(**request.form())
    listing_manager.create_listing(post.email, post.make, post.model, post.year, post.color,
                                   post.car_type, post.price, post.location)
    return RedirectResponse(url="/listings")

    
####### Listings #####################################
