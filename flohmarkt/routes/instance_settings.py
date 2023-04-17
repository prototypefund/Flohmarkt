from fastapi import APIRouter, Body, Depends, Request
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema
from flohmarkt.models.instance_settings import InstanceSettingsSchema, UpdateInstanceSettingsModel
from flohmarkt.auth import get_current_user

router = APIRouter()

@router.post("/", response_description="Nothing")
async def set(request: Request, settings: UpdateInstanceSettingsModel = Body(...), 
                   current_user: UserSchema = Depends(get_current_user)):
    # TODO: check for user being an admin
    settings = jsonable_encoder(settings)
    item["user"] = current_user["id"]
    new_item = await ItemSchema.add(item)
    await post_to_remote(new_item, current_user)
    return new_item

@router.post"/follower")

@router.get("/", response_description="All items")
async def get():
    items = await ItemSchema.retrieve()
    return items
