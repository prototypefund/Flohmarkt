import os
import datetime
import jwt
import crypt
import email_validator
import aiosmtplib
import uuid

from email.mime.text import MIMEText

from fastapi import APIRouter, Body, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from flohmarkt.ratelimit import limiter
from flohmarkt.config import cfg
from flohmarkt.auth import blacklist_token
from flohmarkt.ssl import ssl_context
from flohmarkt.models.user import UserSchema, UpdateUserModel
from flohmarkt.models.instance_settings import get_instance_name
templates = Jinja2Templates(directory="templates")
router = APIRouter()

ACTIVATION_MAIL = """

Heyho {},

thanks for registering with {}.

Please click the following link to complete the registration.

{}/activation/{}

We wish you a pleasant stay on our backyard sale.


Yours, {}
"""

PW_RESET_MAIL = """

Heyho {},

you seem to have forgotten your password and asked us to reset it!
If you did, follow this link to reset your password:

{}/resetpassword/{}

If you did not, please ignore this mail!

Yours, {}
"""

USERNAME_BLACKLIST = [
    "instance"
]

#Registration
@router.get("/register")
async def _(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/registered")
async def _(request: Request):
    return templates.TemplateResponse("registered.html", {"request": request})

@limiter.limit("1/minute")
@router.post("/register")
async def _(request: Request,
                email:str=Form(),
                username:str=Form(),
                password:str=Form(),
                ):

    hostname = cfg["General"]["ExternalURL"]

    email = email.replace(" ","+")

    if "@" in username:
        return {"error": "'@' in username is prohibited"}

    if username in USERNAME_BLACKLIST:
        return {"error": "username is prohibited"}

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
        "admin": False,
        "moderator": False,
        "active": False,
        "activation_code": str(uuid.uuid4()),
        "avatar":None,
        "role":"User",
        "remote_url": f"{hostname}/users/{username}"
    }

    new_user = await UserSchema.add(new_user)
    instance_name = await get_instance_name()


    server = aiosmtplib.SMTP(
        hostname = cfg["SMTP"]["Server"],
        port = int(cfg["SMTP"]["Port"]),
        tls_context = ssl_context,
        username = cfg["SMTP"]["User"],
        password = cfg["SMTP"]["Password"],
    )

    await server.connect()

    text = ACTIVATION_MAIL.format(
            new_user["name"],
            instance_name,
            cfg["General"]["ExternalURL"],
            new_user["activation_code"],
            instance_name
        )
    message = MIMEText(text.encode('utf-8'), _charset='utf-8')
    message["Subject"] = "Registration with {}".format(instance_name)
    await server.sendmail(
        cfg["SMTP"]["From"], 
        email, 
        message.as_string()
    )

    return {"result": True}

@router.get("/resetpassword/{code}")
async def _(request: Request, code : str):
    return templates.TemplateResponse("resetpw.html", {"request": request, "code": code})

@router.post("/resetpassword")
async def _(request: Request, code : str = Form(), password : str = Form()):
    user = await UserSchema.retrieve_single_resetcode(code)
    user["pwhash"] = crypt.crypt(password, crypt.mksalt(method=crypt.METHOD_SHA512,rounds=10000))
    user["reset_token"] = ""
    await UserSchema.update(user["id"], user)

    return {"result": True}

@router.get("/reset_initiated")
async def _(request: Request):
    return templates.TemplateResponse("reset_initiated.html", {"request": request})

@router.get("/forgotpassword")
async def _(request: Request):
    return templates.TemplateResponse("reset.html", {"request": request})

@limiter.limit("1/day")
@router.post("/forgotpassword")
async def _(request: Request, email: str = Form()):
    instance_name = await get_instance_name()
    user = await UserSchema.retrieve_single_email(email)
    if user is not None:
        user["reset_token"] = str(uuid.uuid4())
        await UserSchema.update(user["id"], user)

        server = aiosmtplib.SMTP(
            hostname = cfg["SMTP"]["Server"],
            port = int(cfg["SMTP"]["Port"]),
            tls_context = ssl_context,
            username = cfg["SMTP"]["User"],
            password = cfg["SMTP"]["Password"],
        )

        await server.connect()

        text = PW_RESET_MAIL.format(
                user["name"],
                cfg["General"]["ExternalURL"],
                user["reset_token"],
                instance_name
            )
        message = MIMEText(text.encode('utf-8'), _charset='utf-8')
        message["Subject"] = "Password reset on {}".format(instance_name)
        await server.sendmail(
            cfg["SMTP"]["From"], 
            email, 
            message.as_string()
        )
    return {"result": True}


@router.get("/activation/{activation_code}")
async def _(request : Request, activation_code : str):
    if await UserSchema.activate(activation_code):
        return templates.TemplateResponse("login.html", {"request": request})
    else:
        raise HTTPException(status_code=403, detail="That did not taste very well.")

#Login
@router.post("/token")
async def _(username: str = Form(), password: str = Form()):
    found_user = await UserSchema.retrieve_single_name(username)
    if found_user is None or not found_user["active"]:
        raise HTTPException(status_code=403, detail="Not a valid name-password-pair")

    current_pwhash = crypt.crypt(password, found_user["pwhash"])
    
    if current_pwhash != found_user["pwhash"]:
        raise HTTPException(status_code=403, detail="Not a valid name-password-pair")

    return jwt.encode(
            {
                "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1),
                "user_id": found_user["id"],
                "username": found_user["name"],
                "avatar": found_user["avatar"] if found_user["avatar"] != "" else None,
                "admin": found_user["admin"],
                "moderator": found_user["moderator"],
            },
            cfg["General"]["JwtSecret"],
            algorithm = "HS512"
        )

#Login
@router.get("/login")
async def _(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/blacklist_token")
async def _(request: Request, current_user : UserSchema = Depends(blacklist_token)):
    return {"success":True}

#Logout
@router.get("/logout")
async def _(request: Request):
    return templates.TemplateResponse("logout.html", {"request": request})
