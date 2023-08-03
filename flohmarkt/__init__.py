import asyncio

from fastapi import FastAPI, Request, Response, Depends, Form, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.websockets import WebSocketDisconnect

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from flohmarkt.backgroundjobs import clean_images
from flohmarkt.ratelimit import limiter
from flohmarkt.config import cfg
from flohmarkt.routes.activitypub import item_to_note, user_route, append_context
from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema
from flohmarkt.models.instance_settings import InstanceSettingsSchema
from flohmarkt.routes.item import router as item_router
from flohmarkt.routes.user import router as user_router
from flohmarkt.routes.admin import router as admin_router
from flohmarkt.routes.auth import router as auth_router
from flohmarkt.routes.avatar import router as avatar_router
from flohmarkt.routes.image import router as image_router
from flohmarkt.routes.report import router as report_router
from flohmarkt.routes.webfinger import router as webfinger_router
from flohmarkt.routes.activitypub import router as activitypub_router
from flohmarkt.routes.conversation import router as conversation_router
from flohmarkt.auth import oauth2, get_current_user
from flohmarkt.http import HttpClient
from flohmarkt.socketpool import Socketpool

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.mount("/static", StaticFiles(directory="static"), name="static")
api_prefix = "/api/v1"

app.include_router(item_router, tags=["Item"], prefix=api_prefix+"/item")
app.include_router(image_router, tags=["Image"], prefix=api_prefix+"/image")
app.include_router(user_router, tags=["User"], prefix=api_prefix+"/user")
app.include_router(report_router, tags=["Report"], prefix=api_prefix+"/report")
app.include_router(admin_router, tags=["Admin"], prefix=api_prefix+"/admin")
app.include_router(avatar_router, tags=["Avatar"], prefix=api_prefix+"/avatar")
app.include_router(auth_router, tags=["Auth"], prefix="")
app.include_router(webfinger_router, tags=["Webfinger"], prefix="")
app.include_router(activitypub_router, tags=["Activitypub"], prefix="")
app.include_router(conversation_router, tags=["Conversation"], prefix=api_prefix+"/conversation")


@app.on_event("startup")
async def ini():
    print ("Flohmarkt booting!")
    await HttpClient.initialize()
    print ("Waiting until database gets ready…")
    # TODO implement wait for database
    print ("Database is ready. Proceeding…")
    try:
        instance_settings = await InstanceSettingsSchema.retrieve()
        if not instance_settings["initialized"]:
            hostname = cfg["General"]["ExternalURL"]
            key = instance_settings["initialization_key"]
            print (f"""Flohmarkt is not initialized yet. Please go to 
            {hostname}/setup/{key}
            in order to complete the setup process""")
    except Exception as e:
        await shutdown()
        raise e

    mainloop = asyncio.get_running_loop()
    mainloop.create_task(clean_images())

    
@app.on_event("shutdown")
async def shutdown():
    print ("Tearing down Flohmarkt!")
    asyncio.gather(
        HttpClient.shutdown(),
        Socketpool.shutdown()
    )

@app.get("/")
async def root(request: Request):
    instance_settings = await InstanceSettingsSchema.retrieve()
    adminuser = await UserSchema.retrieve_single_id(instance_settings.get("admin",""))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "adminuser": adminuser,
        "settings": instance_settings,
    })

@app.get("/~{user}/{item}")
async def other(request: Request, user: str, item: str):
    if "application/activity+json" in request.headers["accept"] or \
       "application/ld+json" in request.headers["accept"] or \
       "application/json" in request.headers["accept"]: 
        headers = {"Content-type":"application/activity+json"}
        item = await ItemSchema.retrieve_single_id(item)
        user = await UserSchema.retrieve_single_name(user)
        item = await item_to_note(item, user)
        item = await append_context(item)
        return JSONResponse(content=item, headers=headers)
    else:
        settings = await InstanceSettingsSchema.retrieve()
        item = await ItemSchema.retrieve_single_id(item)
        return templates.TemplateResponse("item.html", {
            "request": request,
            "settings": settings,
            "user": user,
            "item": item
        })

@app.get("/users/{user}/items/{item}")
async def other(request: Request, user: str, item: str):
    if "application/activity+json" in request.headers["accept"]:
        headers = {"Content-type": "application/activity+json" }
    elif "application/ld+json" in request.headers["accept"]:
        headers = {"Content-type": "application/ld+json"}
    elif "application/json" in request.headers["accept"]:
        headers = {"Content-type": "application/json"}
    else:
        raise HTTPException(status_code=400, detail="Only json-based types supported :(")
    item = await ItemSchema.retrieve_single_id(item)
    user = await UserSchema.retrieve_single_name(user)
    item = await item_to_note(item, user)
    item = await append_context(item)
    return JSONResponse(content=item, headers=headers)

@app.get("/~{user}")
async def other(request: Request, user: str):
    if "application/activity+json" in request.headers["accept"]:
        userdata = await user_route(user)
        headers = {"Content-type":"application/activity+json"}
        return JSONResponse(content=userdata, headers=headers)
    user = await UserSchema.retrieve_single_name(user)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found :(")
    settings = await InstanceSettingsSchema.retrieve()
    return templates.TemplateResponse("user.html", {"request": request, "user": user, "settings":settings})


@app.get("/setup/{initkey}")
async def setup_page(request: Request, initkey : str):
    instance_settings = await InstanceSettingsSchema.retrieve()
    if instance_settings["initialization_key"] != initkey:
        raise HTTPException(status_code=403, detail="This is no valid initialization key")
    return templates.TemplateResponse("setup.html", {
        "request": request,
        "settings": instance_settings,
        "initkey": initkey
    })

#Admin
@app.get("/admin")
async def other(request: Request):
    settings = await InstanceSettingsSchema.retrieve()
    admins = await UserSchema.retrieve_admins()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "admins": admins,
        "settings": settings
    })

#Moderation 
@app.get("/moderation")
async def other(request: Request):
    settings = await InstanceSettingsSchema.retrieve()
    return templates.TemplateResponse("moderation.html", {"request": request, "settings": settings})

#Messaging
@app.get("/messages")
async def other(request: Request):
    settings = await InstanceSettingsSchema.retrieve()
    return templates.TemplateResponse("messages.html", {"request": request, "settings": settings})

#New
@app.get("/new")
async def other(request: Request):
    settings = await InstanceSettingsSchema.retrieve()
    return templates.TemplateResponse("new.html", {"request": request, "settings": settings})

#Search
@app.get("/search")
async def other(request: Request, q : str):
    settings = await InstanceSettingsSchema.retrieve()
    return templates.TemplateResponse("search.html", {
        "request": request,
        "settings": settings,
        "searchterm": q
    })

@app.get("/imprint")
async def imprint(request: Request):
    settings = await InstanceSettingsSchema.retrieve()
    i = settings["imprint"]
    return templates.TemplateResponse("imprint.html", {
        "request": request,
        "settings": settings,
        "imprint": i
    })

@app.get("/privacy")
async def privacy(request: Request):
    settings = await InstanceSettingsSchema.retrieve()
    p = settings["privacy"]
    return templates.TemplateResponse("privacy.html", {
        "request": request,
        "settings": settings,
        "privacy": p
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    authenticated = False
    while True:
        try:
            data = await websocket.receive_text()
            if not authenticated:
                user = await get_current_user(data) # first data must be token
                if user is None:
                    websocket.close()
                    break
                else:
                    authenticated = True
                    Socketpool.add_socket(user, websocket)
                    #await websocket.send_json({"msg":"Welcome to the server","head":"Authenticated!"})
        except (WebSocketDisconnect, RuntimeError):
            print("Websocket connection closed")
            break
                
