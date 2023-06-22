from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema, UpdateUserModel
from flohmarkt.auth import oauth2, get_current_user

router = APIRouter()

@router.get("/", response_description="All users")
async def get_users(current_user : UserSchema = Depends(get_current_user)):
    if not (current_user["admin"] or current_user["moderator"]):
        raise HTTPException(status_code=403, detail="Only admins/mods :(")
    users = await UserSchema.retrieve()
    for user in users:
        await UserSchema.filter(user)
    return users

@router.get("/{ident}", response_description="A single user if any")
async def get_user(ident:str):
    user = await UserSchema.retrieve_single_id(ident)
    if user is None:
        raise HTTPException(status_code=404, detail="User is not here :(")
    await UserSchema.filter(user)
    return user

@router.put("/{ident}", response_description="Update stuff")
async def update_user(ident: str, req: dict = Body(...),current_user : UserSchema = Depends(get_current_user)):
    if ident != current_user["id"]:
        return HTTPException(status_code=403, detail="Cant override other users properties")
    #req = {k: v for k,v in req.dict().users() if v is not None}
    updated_user = await UserSchema.update(ident, req)
    if updated_user:
        return updated_user
    raise HTTPException(status_code=500, detail="Something went wrong :(")

@router.delete("/{ident}", response_description="deleted")
async def delete_user(ident: str):
    await UserSchema.delete(ident)
    return "SUS"
