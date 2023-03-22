import uuid

from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema, UpdateUserModel
from flohmarkt.auth import oauth2, get_current_user

router = APIRouter()

@router.post("/", response_description="Image upload")
async def get_users(current_user : UserSchema = Depends(get_current_user), image: bytes = Body(...)):
    users = await UserSchema.retrieve()
    return str(uuid.uuid4())

@router.get("/{ident}", response_description="Get an image")
async def get_users(ident: str):
    return b"PNG LOL"
