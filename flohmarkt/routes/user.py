from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema, UpdateUserModel

router = APIRouter()

@router.post("/", response_description="Added")
async def add_user(user: UserSchema = Body(...)):
    user = jsonable_encoder(user)
    new_user = await UserSchema.add(user)
    return new_user

@router.get("/", response_description="All users")
async def get_users():
    users = await UserSchema.retrieve()
    return users

@router.get("/{ident}", response_description="A single user if any")
async def get_user(ident:str):
    print("IN ROUTE", ident)
    user = await UserSchema.retrieve_single(ident)
    return user

@router.put("/{ident}", response_description="Update stuff")
async def update_user(ident: str, req: UpdateUserModel = Body(...)):
    req = {k: v for k,v in req.dict().users() if v is not None}
    updated_user = await UserSchema.update(ident, req)
    if updated_user:
        return "YEEEH"
    return "NOOO"

@router.delete("/{ident}", response_description="deleted")
async def delete_user(ident: str):
    await UserSchema.delete(ident)
    return "SUS"
