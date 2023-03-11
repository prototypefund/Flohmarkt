from fastapi import APIRouter, Body, Request, Form
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
                password1:str=Form(),
                password2:str=Form()
                ):
    print(email, username, password1, password2)
    if password1 != password2 or password1 == "" and password2 == "":
        return templates.TemplateResponse("register.html", {"request":request})
    if username == "":
        return templates.TemplateResponse("register.html", {"request":request})
    try:
        email_validator.validate_email(email)
    except:
        return templates.TemplateResponse("register.html", {"request":request})

    # TODO: check for 
    found_for_email = UserSchema.retrieve_single_email(email)
    found_for_name = UserSchema.retrieve_single_email(username)

    if found_for_name is not None or found_for_email is not None:
        return templates.TemplateResponse("register.html", {"request":request})

    return templates.TemplateResponse("registered.html", {"request":request})

#Login
@router.post("/token")
async def other(username: str = Form(), password: str = Form()):
    if username != "reyna" or password != "skye":
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
