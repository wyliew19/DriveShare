from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from driveshare.utils.user import UserMediator
from driveshare.utils.listing import ListingMediator
from driveshare.models.basemodels import ListingPost
from driveshare.models.user import User
from driveshare.security.payment import PaymentProxy
from driveshare.di import get_current_user, get_user_manager, get_listing_manager

# Create a FastAPI instance with session middleware and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="driveshare/templates")

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
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

####### Login Page and Authentication ##############

####### Logout #####################################

@app.post("/logout")
def logout(request: Request):
    pass

####### Logout #####################################

####### Payment ####################################

@app.get("/payment/auth", response_class=HTMLResponse)
def authorize(request: Request):
    return templates.TemplateResponse("authorize.html", {"request": request})

@app.post("/payment/auth")
def payment(password: Annotated[str, Form], user = Depends(get_current_user)):
    proxy = PaymentProxy(user.email)
    return proxy.authorize(password)

@app.get("/payment", response_class=HTMLResponse)
def payment(request: Request):
    return templates.TemplateResponse("payment.html", {"request": request})

@app.get("/payment_confirmation")
def payment_confirmation(request: Request):
    return templates.TemplateResponse("payment_confirmation.html", {"request": request})

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

@app.get("/listings/{id}", response_class=HTMLResponse)
def listing(request: Request, id: int, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    listing = listing_manager.get_listing(id)
    return templates.TemplateResponse("listing.html", {"request": request, "listing": listing})

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
