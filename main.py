from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from driveshare.utils.user import UserMediator
from driveshare.utils.listing import ListingMediator
from driveshare.models.basemodels import ListingPost
from driveshare.security.cookie import SessionHandler
from driveshare.security.payment import PaymentProxy

# Create a FastAPI instance with session middleware and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="driveshare/templates")

# Backend managers
user_manager = UserMediator()
listing_manager = ListingMediator()
session_handler = SessionHandler()

####### Root Page ##################################
@app.get("/", response_class=HTMLResponse)
def registration(request: Request):
    return templates.TemplateResponse("Registration.html", {"request": request})

####### Login Page and Authentication ##############
@app.get("/login_page/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login/")
def login(email: str = Form(...), password: str = Form(...)):
    try:
        authentication = user_manager.login(email, password)
        if authentication:
            redirect_url = f"/home" # Redirect to the home page after successful login
            return session_handler.get_cookied_redirect(url=redirect_url, value=email)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/home", response_class=HTMLResponse)
def handle_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
####### Login Page and Authentication ##############

@app.post("/logout/")
def logout(request: Request):
    email = session_handler.get_cookie(request)
    session_handler.remove_session(email)
    return RedirectResponse(url="/")

####### Payment ####################################

@app.get("/payment/auth", response_class=HTMLResponse)
def authorize(request: Request):
    return templates.TemplateResponse("authorize.html", {"request": request})

@app.post("/payment/auth")
def payment(request: Request, password: str = Form(...)):
    proxy = PaymentProxy(session_handler.get_cookie(request))
    return proxy.authorize(password)

@app.get("/payment/", response_class=HTMLResponse)
def payment(request: Request):
    return templates.TemplateResponse("payment.html", {"request": request})

@app.get("/payment_confirmation/")
def payment_confirmation(request: Request):
    return templates.TemplateResponse("payment_confirmation.html", {"request": request})

####### Payment ####################################

####### Registration ###############################

@app.post("/register/", response_class=RedirectResponse)
def register(email: str = Form(...), password: str = Form(...)):
    try:
        user_manager.register(email, password)
        redirect_url = f"/register_confirmation"
        return session_handler.get_cookied_redirect(url=redirect_url, value=email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/register_confirmation", response_class=HTMLResponse)
def handle_registration_confirmation(request: Request):
    return templates.TemplateResponse("registration_confirmation.html", {"request": request})

@app.get("/home_page/", response_class=HTMLResponse)
def handle_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

####### Registration ################################

####### Listings #####################################

@app.get("/listings", response_class=HTMLResponse)
def listings(request: Request):
    listings = listing_manager.get_listings()
    return templates.TemplateResponse("listings.html", {"request": request, "listings": listings})

@app.get("/listings/{id}", response_class=HTMLResponse)
def listing(request: Request, id: int):
    listing = listing_manager.get_listing(id)
    return templates.TemplateResponse("listing.html", {"request": request, "listing": listing})

@app.get("/listings/post", response_class=HTMLResponse)
def post_listing(request: Request):
    return templates.TemplateResponse("post_listing.html", {"request": request})

@app.post("/listings/post")
def post_listing(request: Request):
    post = ListingPost(**request.form())
    listing_manager.create_listing(post.email, post.make, post.model, post.year, post.color,
                                   post.car_type, post.price, post.location)
    return RedirectResponse(url="/listings")

    
####### Listings #####################################