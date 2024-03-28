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