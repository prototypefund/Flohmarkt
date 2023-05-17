import os
import datetime
import jwt
import crypt
import email_validator
import smtplib
import uuid

from email.mime.text import MIMEText

from fastapi import APIRouter, Body, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.ssl import ssl_context
from flohmarkt.models.user import UserSchema, UpdateUserModel
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

@router.post("/register")
async def _(request: Request,
                email:str=Form(),
                username:str=Form(),
                password:str=Form(),
                ):

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
        "role":"User"
    }

    new_user = await UserSchema.add(new_user)

    server = smtplib.SMTP(cfg["SMTP"]["Server"], int(cfg["SMTP"]["Port"]))

    server.ehlo()
    server.starttls(context=ssl_context)
    server.ehlo()
    server.login(cfg["SMTP"]["User"], cfg["SMTP"]["Password"])
    text = ACTIVATION_MAIL.format(
            new_user["name"],
            cfg["General"]["InstanceName"],
            cfg["General"]["ExternalURL"],
            new_user["activation_code"],
            cfg["General"]["InstanceName"]
        )
    message = MIMEText(text.encode('utf-8'), _charset='utf-8')
    message["Subject"] = "Registration with {}".format(cfg["General"]["InstanceName"])
    server.sendmail(
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
            },
            cfg["General"]["JwtSecret"],
            algorithm = "HS512"
        )

#Login
@router.get("/login")
async def _(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

#Logout
@router.get("/logout")
async def _(request: Request):
    return templates.TemplateResponse("logout.html", {"request": request})
