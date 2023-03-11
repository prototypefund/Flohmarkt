import jwt
import datetime

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer

from flohmarkt.routes.item import router as item_router
from flohmarkt.routes.user import router as user_router

templates = Jinja2Templates(directory="templates")

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
api_prefix = "/api/v1"

app.include_router(item_router, tags=["Item"], prefix=api_prefix+"/item")
app.include_router(user_router, tags=["User"], prefix=api_prefix+"/user")

@app.on_event("startup")
async def ini():
    print ("Flohmarkt booting!")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/~{user}/{item}")
async def other(request: Request, user: str, item: str):
    return templates.TemplateResponse("item.html", {"request": request, "user": user, "item": item})

@app.get("/~{user}")
async def other(request: Request, user: str):
    return templates.TemplateResponse("user.html", {"request": request, "user": user})

#Registration
@app.get("/register")
async def other(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def other(request: Request):
    return templates.TemplateResponse("registered.html", {"request": request})

#Login
@app.post("/token")
async def other(username: str = Form(), password: str = Form()):
    if username != "reyna" or password != "skye":
        raise HTTPException(status_code=403, detail="Not a valid name-password-pair")
    return jwt.encode(
            {"exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)},
            "yolosecret"
        )

#Login
@app.get("/login")
async def other(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#Logout
@app.get("/logout")
async def other(toast_id:int):
    return {"message": "1 toast"}
