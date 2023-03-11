
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from flohmarkt.routes.item import router as item_router
from flohmarkt.routes.user import router as user_router

templates = Jinja2Templates(directory="templates")

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

@app.get("/u/{toast_id}")
async def other(toast_id:int):
    return {"message": "1 toast"}

@app.get("/register")
async def other(toast_id:int):
    return {"message": "1 toast"}

@app.get("/signin")
async def other(toast_id:int):
    return {"message": "1 toast"}
