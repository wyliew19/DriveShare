from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from user_registration import User
from pydantic import BaseModel

app = FastAPI()
user_manager = User()
templates = Jinja2Templates(directory="driveshare/templates")

class RegistrationForm(BaseModel):
    email: str
    password: str

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
            redirect_url = f"/home"  # Redirect to the home page after successful login
            return RedirectResponse(url=redirect_url)
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/home", response_class=HTMLResponse)
def handle_login_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
####### Login Page and Authentication ##############

####### Registration ###################################
@app.post("/register/")
def register(email: str = Form(...), password: str = Form(...)):
    try:
        user_manager.register(email, password)
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
def login_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
####### Registration ###################################
