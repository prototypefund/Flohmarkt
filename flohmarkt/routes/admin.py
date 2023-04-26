from fastapi import APIRouter, Body, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.auth import get_current_user
from flohmarkt.models.instance_settings import InstanceSettingsSchema, UpdateInstanceSettingsModel
from flohmarkt.models.user import UserSchema


router = APIRouter()

@router.post("/", response_description="Update instance settings")
async def set_instancesettings(request: Request, settings: UpdateInstanceSettingsModel = Body(...), 
                   current_user: UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    instance_settings = await InstanceSettingsSchema.retrieve()
    instance_settings.update(settings)
    await InstanceSettingsSchema.set(instance_settings)
    return instance_settings

@router.get("/toggle_admin/{user_id}", response_description="A boolean representing the users new admin state")
async def toogle_admin(user_id, current_user : UserSchema = Depends(get_current_user)):
    print("HEMLO")
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    user = await UserSchema.retrieve_single_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not here :(")
    if current_user == user:
        raise HTTPException(status_code=403, detail="Admins are not allowed to de-admin themselves")
    user["admin"] = not user["admin"]
    res = await UserSchema.update(user_id, user)
    if res:
        return {"admin": user["admin"]}
    else:
        return {"admin": not user["admin"]}

@router.get("/toggle_moderator/{user_id}", response_description="A boolean representing the users new moderator state")
async def toogle_moderator(user_id, current_user : UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    user = await UserSchema.retrieve_single_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not here :(")
    user["moderator"] = not user["moderator"]
    res = await UserSchema.update(user_id, user)
    if res:
        return {"moderator": user["moderator"]}
    else:
        return {"moderator": not user["moderator"]}
