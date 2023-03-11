import datetime
import jwt
import crypt
import email_validator

from fastapi import APIRouter, Body, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema, UpdateUserModel
templates = Jinja2Templates(directory="templates")
router = APIRouter()

#Registration
@router.get("/register")
async def other(request: Request):
    return templates.TemplateResponse("register.html", {"request":request})

@router.post("/register")
async def other(request: Request,
                email:str=Form(),
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
        "avatar":None,
        "role":"User"
    }

    new_user_foo = await UserSchema.add(new_user)

    return {"result": True}

#Login
@router.post("/token")
async def other(username: str = Form(), password: str = Form()):
    found_user = await UserSchema.retrieve_single_name(username)
    if found_user is None:
        raise HTTPException(status_code=403, detail="Not a valid name-password-pair")

    current_pwhash = crypt.crypt(password, found_user["pwhash"])
    
    if current_pwhash != found_user["pwhash"]:
        raise HTTPException(status_code=403, detail="Not a valid name-password-pair")

    return jwt.encode(
            {"exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)},
            "yolosecret"
        )

#Login
@router.get("/login")
async def other(request: Request):
    return templates.TemplateResponse("login.html", {"request":request})

#Logout
@router.get("/logout")
async def other(toast_id:int):
    return {"message": "1 toast"}
