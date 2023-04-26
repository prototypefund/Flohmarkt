import json
import email_validator
import crypt

from fastapi import FastAPI, Request, Response, Depends, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from flohmarkt.config import cfg
from flohmarkt.routes.activitypub import get_item_activity
from flohmarkt.models.user import UserSchema
from flohmarkt.models.instance_settings import InstanceSettingsSchema
from flohmarkt.routes.item import router as item_router
from flohmarkt.routes.user import router as user_router
from flohmarkt.routes.admin import router as admin_router
from flohmarkt.routes.auth import router as auth_router
from flohmarkt.routes.image import router as image_router
from flohmarkt.routes.webfinger import router as webfinger_router
from flohmarkt.routes.activitypub import router as activitypub_router
from flohmarkt.routes.conversation import router as conversation_router
from flohmarkt.auth import oauth2, get_current_user
from flohmarkt.http import HttpClient

templates = Jinja2Templates(directory="templates")

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
api_prefix = "/api/v1"

app.include_router(item_router, tags=["Item"], prefix=api_prefix+"/item")
app.include_router(image_router, tags=["Image"], prefix=api_prefix+"/image")
app.include_router(user_router, tags=["User"], prefix=api_prefix+"/user")
app.include_router(admin_router, tags=["Admin"], prefix=api_prefix+"/admin")
app.include_router(auth_router, tags=["Auth"], prefix="")
app.include_router(webfinger_router, tags=["Webfinger"], prefix="")
app.include_router(activitypub_router, tags=["Activitypub"], prefix="")
app.include_router(conversation_router, tags=["Conversation"], prefix=api_prefix+"/conversation")

@app.on_event("startup")
async def ini():
    print ("Flohmarkt booting!")
    await HttpClient.initialize()
    try:
        instance_settings = await InstanceSettingsSchema.retrieve()
        if not instance_settings["initialized"]:
            hostname = cfg["General"]["ExternalURL"]
            key = instance_settings["initialization_key"]
            print (f"""Flohmarkt is not initialized yet. Please go to 
            {hostname}/setup/{key}
            in order to complete the setup process""")
    except:
        shutdown()

    
@app.on_event("shutdown")
async def shutdown():
    print ("Tearing down Flohmarkt!")
    await HttpClient.shutdown()

@app.get("/")
async def root(request: Request):
    instance_settings = await InstanceSettingsSchema.retrieve()
    return templates.TemplateResponse("index.html", {"request": request, "settings": instance_settings})

@app.get("/~{user}/{item}")
async def other(request: Request, user: str, item: str):
    print(request.headers["accept"])
    if "application/activity+json" in request.headers["accept"]:
        item = await get_item_activity(item, user)
        print(json.dumps(item))
        item = json.dumps(item)
        return Response(content=item, media_type="application/activity+json, application/ld+json")
    return templates.TemplateResponse("item.html", {"request": request, "user": user, "item": item})

@app.get("/~{user}")
async def other(request: Request, user: str):
    user = await UserSchema.retrieve_single_name(user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found :(")
    return templates.TemplateResponse("user.html", {"request": request, "user": user})


@app.get("/setup/{initkey}")
async def setup_page(request: Request, initkey : str):
    instance_settings = await InstanceSettingsSchema.retrieve()
    if instance_settings["initialization_key"] != initkey:
        raise HTTPException(status_code=403, detail="This is no valid initialization key")
    return templates.TemplateResponse("setup.html", {"request": request, "initkey": initkey})

@app.post("/setup/{initkey}/")
async def setup_execute(request: Request, initkey : str,
                email:str=Form(),
                instancename:str=Form(),
                username:str=Form(),
                password:str=Form(),
    ):
    email = email.replace(" ","+")

    if username == "" or password == "":
        return {"error": "username or password empty"}
    try:
        email_validator.validate_email(email)
    except email_validator.EmailNotValidError as e:
        return {"error": "email invalid "+str(e)+"'"+email+"'"}

    found_for_email = await UserSchema.retrieve_single_email(email)
    found_for_name = await UserSchema.retrieve_single_email(username)
    
    if found_for_name is not None or found_for_email is not None:
        return {"error": "user already exists"}

    pwhash = crypt.crypt(password, crypt.mksalt(method=crypt.METHOD_SHA512,rounds=10000))

    new_user = {
        "email":email,
        "name":username,
        "pwhash":pwhash,
        "active": True,
        "admin": True,
        "moderator": True,
        "avatar":None,
        "role":"User"
    }

    new_user = await UserSchema.add(new_user)

    instance_settings = await InstanceSettingsSchema.retrieve()
    instance_settings["name"] = instancename
    instance_settings["initialized"] = True
    instance_settings["initialization_key"] = ""

    await InstanceSettingsSchema.set(instance_settings)

    return {"ok": True}

#Admin
@app.get("/admin")
async def other(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

#New
@app.get("/new")
async def other(request: Request):
    return templates.TemplateResponse("new.html", {"request": request})

#Search
@app.get("/search")
async def other(request: Request, q : str):
    return templates.TemplateResponse("search.html", {"request": request, "searchterm": q})
