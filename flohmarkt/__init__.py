from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from flohmarkt.routes.item import router as item_router
from flohmarkt.routes.user import router as user_router
from flohmarkt.routes.auth import router as auth_router
from flohmarkt.auth import oauth2, get_current_user
from flohmarkt.db import Database

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
api_prefix = "/api/v1"

app.include_router(item_router, tags=["Item"], prefix=api_prefix+"/item")
app.include_router(user_router, tags=["User"], prefix=api_prefix+"/user")
app.include_router(auth_router, tags=["Auth"], prefix="")

@app.on_event("startup")
async def ini():
    print ("Flohmarkt booting!")
    await Database.initialize()
    
@app.on_event("shutdown")
async def ini():
    print ("Tearing down Flohmarkt!")
    await Database.shutdown()

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/~{user}/{item}")
async def other(request: Request, user: str, item: str):
    return templates.TemplateResponse("item.html", {"request": request, "user": user, "item": item})

@app.get("/~{user}")
async def other(request: Request, user: str):
    return templates.TemplateResponse("user.html", {"request": request, "user": user})

#Admin
@app.get("/admin")
async def other(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

#New
@app.get("/new")
async def other(request: Request):
    return templates.TemplateResponse("new.html", {"request": request})
