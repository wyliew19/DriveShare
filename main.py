from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from driveshare.utils.user import UserSingleton
from driveshare.utils.listing import ListingManager

# Create a FastAPI instance with session middleware and Jinja2 templates
app = FastAPI()
templates = Jinja2Templates(directory="driveshare/templates")

# Backend managers
user_manager = UserSingleton()
listing_manager = ListingManager()


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
            return RedirectResponse(url=redirect_url)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/home", response_class=HTMLResponse)
def handle_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
####### Login Page and Authentication ##############

####### Registration ###############################
@app.post("/register/")
def register(request: Request, email: str = Form(...), password: str = Form(...)):
    try:
        id = user_manager.register(email, password).id
        redirect_url = f"/register_confirmation"
        return RedirectResponse(url=redirect_url)
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


@app.get("/listing_confirmation", response_class=HTMLResponse)
def listing_confirmation(request: Request):
    return templates.TemplateResponse("listing_confirmation.html", {"request": request})

@app.post("/create_listing/")
def create_listing(seller_id: int = Form(...), make: str = Form(...), model: str = Form(...), year: int = Form(...), color: str = Form(...), car_type: str = Form(...), price: float = Form(...), location: str = Form(...)):
    try:
        listing_manager.create_listing(seller_id, make, model, year, color, car_type, price, location)
        redirect_url = f"/listing_confirmation"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))