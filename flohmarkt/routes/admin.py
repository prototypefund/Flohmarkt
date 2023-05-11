from fastapi import APIRouter, Body, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.auth import get_current_user
from flohmarkt.models.instance_settings import InstanceSettingsSchema, UpdateInstanceSettingsModel
from flohmarkt.models.user import UserSchema
from flohmarkt.models.follow import FollowSchema
from flohmarkt.http import HttpClient


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

@router.get("/", response_description="Current instance settings")
async def set_instancesettings(current_user: UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    return await InstanceSettingsSchema.retrieve()

@router.get("/follow_instance/", response_description="The current list of followed instances")
async def follow_instance(url : str, current_user: UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    instance_settings = await InstanceSettingsSchema.retrieve()
    for follow in instance_settings["pending_following"]:
        if follow == url:
            return instance_settings["pending_following"]

    #TODO: try to connect and webfinger the shit out of the other instance

    instance_settings["pending_following"].append(url)
    await InstanceSettingsSchema.set(instance_settings)

    hostname = cfg["General"]["ExternalURL"]

    follow = FollowSchema(
        context= "https://www.w3.org/ns/activitystreams",
        id= hostname + "/users/instance#follows/42",
        type= "Follow",
        actor= hostname+"/users/instance",
        object= url+"/users/instance"
    )

    print(follow)

    headers = {
        "Content-Type":"application/json"
    }
    sign("post", url + "/inbox", headers, json.dumps(accept), user)
    async with HttpClient().post(rcv_inbox, data=json.dumps(accept), headers = headers) as resp:
        print(resp.status)
        if resp.status != 200:
            raise HTTPException(status_code=400, detail=f"Received {resp.status} upon accepting")
    
    return instance_settings["pending_following"]

@router.get("/unfollow_instance/", response_description="The current list of followed instances")
async def unfollow_instance(url : str, current_user: UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    instance_settings = await InstanceSettingsSchema.retrieve()

    found = False
    if url in instance_settings["following"]:
        instance_settings["following"].remove(url)
        found = True
    if url in instance_settings["pending_following"]:
        instance_settings["pending_following"].remove(url)
        found = True
    if not found:
        raise HTTPException(status_code=404, detail="This instance is not being followed")

    await InstanceSettingsSchema.set(instance_settings)

    return instance_settings["following"]

    

@router.get("/toggle_admin/{user_id}", response_description="A boolean representing the users new admin state")
async def toogle_admin(user_id, current_user : UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    user = await UserSchema.retrieve_single_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not here :(")
    if current_user == user:
        raise HTTPException(status_code=403, detail="Admins are not allowed to de-admin themselves")
    user["admin"] = not user.get("admin",False)
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
    user["moderator"] = not user.get("moderator", False)
    res = await UserSchema.update(user_id, user)
    if res:
        return {"moderator": user["moderator"]}
    else:
        return {"moderator": not user["moderator"]}
