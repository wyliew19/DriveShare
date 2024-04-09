from typing import Annotated
from pathlib import Path
from datetime import datetime
from math import floor

from fastapi import FastAPI, HTTPException, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm

from driveshare.utils.user import UserMediator
from driveshare.utils.listing import ListingMediator
from driveshare.models.posts import ListingPost, FilterSettings, SecurityQuestionForm, as_dict
from driveshare.models.user import User
from driveshare.security.payment import PaymentProxy
from driveshare.security.cor import SecurityQuestion1Handler, SecurityQuestion2Handler, SecurityQuestion3Handler
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

@app.get("/payment/auth/", response_class=HTMLResponse)
def authorize(request: Request, listing_id: int, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
              user = Depends(get_current_user)):
    listing = listing_manager.get_listing(listing_id)
    strip_date = lambda x: datetime.strptime(x, "%Y-%m-%d")
    start_date = strip_date(listing.availability.start_date)
    end_date = strip_date(listing.availability.end_date)

    # Determine the maximum number of days the user can rent the car
    max_days = (end_date - start_date).days
    max_days = max_days if max_days > 0 else 1
    max_days = floor(min(user.balance / listing.car.price, max_days))
    return templates.TemplateResponse("payment.html", {"request": request, "user": user, "max_days": max_days, "listing": listing})

@app.post("/payment/auth")
def payment(password: Annotated[str, Form(...)], days: Annotated[int, Form(...)],
            listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
            listing_id: int, user: Annotated[User, Depends(get_current_user)]):
    return listing_manager.purchase_listing(password, listing_id, user.id, days)

@app.get("/payment_confirmation")
def payment_confirmation(request: Request, amount: str, user: Annotated[User, Depends(get_current_user)]):
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

####### Security Questions ###########################

@app.get("/securityQuestions", response_class=HTMLResponse)
def handle_security_questionPage(request: Request):
    return templates.TemplateResponse("security_questions.html", {"request": request})

@app.post("/securityQuestions")
async def handle_security_questions(answers: Annotated[SecurityQuestionForm, Depends()],
                                    user_manager: Annotated[UserMediator, Depends(get_user_manager)], user = Depends(get_current_user)):
    try:
        user_manager.securityAnswers(user.id, answers.security_answer1, answers.security_answer2, answers.security_answer3)
        redirect_url = f"/register_confirmation/"
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

####### Security Questions ###########################

######## Password Recovery ###########################

@app.get("/password_recovery", response_class=HTMLResponse)
def password_recovery(request: Request):
    return templates.TemplateResponse("password_recovery.html", {"request": request})

@app.post("/password_recovery") 
def password_recovery(answers: Annotated[SecurityQuestionForm, Depends()], email: str = Form(...)):

    # Create the chain of responsibility
    handler1 = SecurityQuestion1Handler()
    handler2 = SecurityQuestion2Handler(handler1)
    handler3 = SecurityQuestion3Handler(handler2)

    # Check the answers
    answers = [answers.security_answer1, answers.security_answer2, answers.security_answer3]
    for i, answer in enumerate(answers):
        if not handler3.handle(email, answer):
            raise HTTPException(status_code=400, detail="Incorrect answer")
    response = RedirectResponse(url="/password_recovery_confirmation/")
    response.set_cookie(key="email", value=email)
    return response

@app.post("/password_recovery_confirmation/", response_class=HTMLResponse)
def password_recovery_confirmation(request: Request):
    return templates.TemplateResponse("password_recovery_confirmation.html", {"request": request})

@app.get("/new_password/", response_class=RedirectResponse)
async def new_password(request: Request, user_manager: Annotated[UserMediator, Depends(get_user_manager)],
                       password: str = Form(...)):
    try:
        email = request.cookies.get("email")
        user_manager.new_password(email, password)
        redirect_url = f"/login_page"
        response = RedirectResponse(url=redirect_url)
        response.delete_cookie("email")
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
######## Password Recovery ##########################


####### Listings #####################################

@app.get("/listings", response_class=HTMLResponse)
def listings(request: Request, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
             user = Depends(get_current_user)):
    listings = listing_manager.get_listings()
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "user": user})

@app.post("/listings", response_class=HTMLResponse)
def filter_listings(request: Request, filters: Annotated[FilterSettings, Depends()], listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
                    user = Depends(get_current_user)):
    filters = as_dict(filters)
    listings = listing_manager.get_listings(filters=filters)
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "user": user})

@app.get("/listings/{id}", response_class=HTMLResponse)
def listing(request: Request, id: int, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
            user_manager: Annotated[UserMediator, Depends(get_user_manager)], user = Depends(get_current_user)):
    listing = listing_manager.get_listing(id)
    seller_email = user_manager[listing.seller_id].email

    return templates.TemplateResponse("single_listing.html", {"request": request, "listing": listing, "user": user, 
                                                              "seller_email": seller_email, "ratings": listing_manager.get_rating(listing.seller_id)})

@app.get("/my_listings", response_class=HTMLResponse)
def my_listings(request: Request, user: Annotated[User, Depends(get_current_user)], listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    listings = listing_manager.get_listings(id=user.id)
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "user": user})

@app.post("/my_listings", response_class=HTMLResponse)
def filter_my_listings(request: Request, user: Annotated[User, Depends(get_current_user)], filters: Annotated[FilterSettings, Depends()],
                       listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    filters = as_dict(filters)
    listings = listing_manager.get_listings(id=user.id, filters=filters)
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "user": user})

@app.get("/listing/post", response_class=HTMLResponse)
def post_listing(request: Request, user = Depends(get_current_user)):
    return templates.TemplateResponse("post_listing.html", {"request": request, "user": user})

@app.post("/listing/post")
def post_listing(listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
                 post: Annotated[ListingPost, Depends()], user = Depends(get_current_user)):
    listing_manager.create_listing(user.email, post.make, post.model, post.year, post.color, post.car_type,
                                   post.price, post.city, post.state, post.start_date, post.end_date)
    return {"status": "success"}

    
####### Listings #####################################

####### Rental History ###############################

@app.get("/rental_history", response_class=HTMLResponse)
def rental_history(request: Request, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
                   user = Depends(get_current_user)):
    listings = listing_manager.get_purchase_history(user.id)
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "user": user})

@app.post("/rental_history", response_class=HTMLResponse)
def filter_rental_history(request: Request, filters: Annotated[FilterSettings, Depends()], listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)],
                          user = Depends(get_current_user)):
    filters = as_dict(filters)
    listings = listing_manager.get_purchase_history(user.id, filters=filters)
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings, "user": user})

@app.post("/rate_listing/{id}")
def rate_listing(id: int, rating: int, listing_manager: Annotated[ListingMediator, Depends(get_listing_manager)]):
    if rating not in [0, 1]:
        raise HTTPException(status_code=400, detail="Invalid rating")
    rating = bool(rating)
    listing_manager.rate_listing(id, rating)
    return {"message": "success"}

####### Add balance ##################################
@app.post("/add_balance")
def add_balance(amount: Annotated[float, Form(...)], user_manager: Annotated[UserMediator, Depends(get_user_manager)], user = Depends(get_current_user)):
    start_balance = user_manager.get_balance(user.email)
    user_manager.add_balance(user.email, amount)
    if start_balance == user_manager.get_balance(user.email) - amount:
        return {"status": "success"}
    return {"status": "failure"}

####### Add balance ##################################

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)