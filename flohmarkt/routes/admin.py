import json
import crypt
import email_validator

from fastapi import APIRouter, Body, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.auth import get_current_user
from flohmarkt.models.instance_settings import InstanceSettingsSchema, UpdateInstanceSettingsModel, Coordinates
from flohmarkt.models.user import UserSchema
from flohmarkt.models.follow import FollowSchema, AcceptSchema
from flohmarkt.http import HttpClient
from flohmarkt.signatures import sign


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

    instance_user = await UserSchema.retrieve_single_name("instance")

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

    follow = jsonable_encoder(follow)

    print(follow)

    headers = {
        "Content-Type":"application/json"
    }
    sign("post", url + "/inbox", headers, json.dumps(follow), instance_user)
    async with HttpClient().post(url + "/inbox", data=json.dumps(follow), headers = headers) as resp:
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

@router.get("/remove_instance/", response_description="The current list of followed instances")
async def unfollow_instance(url : str, current_user: UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    instance_settings = await InstanceSettingsSchema.retrieve()

    if url in instance_settings["followers"]:
        instance_settings["followers"].remove(url)
    else:
        raise HTTPException(status_code=404, detail="This instance is not a follower")

    await InstanceSettingsSchema.set(instance_settings)

    return instance_settings["following"]


@router.get("/reject_instance/", response_description="The current list of followed instances")
async def reject_instance(url : str, current_user: UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    instance_settings = await InstanceSettingsSchema.retrieve()

    if url not in instance_settings["pending_followers"]:
        raise HTTPException(status_code=403, detail="This is not a follower candidate")

    instance_settings["pending_followers"].remove(url)

    await InstanceSettingsSchema.set(instance_settings)

    instance_user = await UserSchema.retrieve_single_name("instance")

    hostname = cfg["General"]["ExternalURL"]
    follow = FollowSchema(
        context= "https://www.w3.org/ns/activitystreams",
        id= url + "/users/instance#follows/42",
        type= "Follow",
        actor= url +"/users/instance",
        object= hostname +"/users/instance"
    )
    accept = AcceptSchema(
        object=follow,
        id = f"{hostname}/users/instance#accepts/follows/42",
        type = "Reject",
        actor = f"{hostname}/users/instance",
        context = "https://www.w3.org/ns/activitystreams"
    )
    accept = jsonable_encoder(accept)
    headers = {
        "Content-Type":"application/json"
    }
    sign("post", url+"/inbox", headers, json.dumps(accept), instance_user)
    async with HttpClient().post(url+"/inbox", data=json.dumps(accept), headers = headers) as resp:
        if resp.status != 200:
            raise HTTPException(status_code=400, detail=f"Received {resp.status} upon accepting")
        return

    return instance_settings["following"]
    

@router.get("/accept_instance/", response_description="The current list of followed instances")
async def accept_instance(url : str, current_user: UserSchema = Depends(get_current_user)):
    if not current_user["admin"]:
        raise HTTPException(status_code=403, detail="Only admins may do this")
    instance_settings = await InstanceSettingsSchema.retrieve()

    if url not in instance_settings["pending_followers"]:
        raise HTTPException(status_code=403, detail="This is not a follower candidate")

    instance_settings["pending_followers"].remove(url)
    if url not in instance_settings["followers"]:
        instance_settings["followers"].append(url)

    await InstanceSettingsSchema.set(instance_settings)

    instance_user = await UserSchema.retrieve_single_name("instance")

    hostname = cfg["General"]["ExternalURL"]
    follow = FollowSchema(
        context= "https://www.w3.org/ns/activitystreams",
        id= url + "/users/instance#follows/42",
        type= "Follow",
        actor= url +"/users/instance",
        object= hostname +"/users/instance"
    )
    accept = AcceptSchema(
        object=follow,
        id = f"{hostname}/users/instance#accepts/follows/42",
        type = "Accept",
        actor = f"{hostname}/users/instance",
        context = "https://www.w3.org/ns/activitystreams"
    )
    accept = jsonable_encoder(accept)
    headers = {
        "Content-Type":"application/json"
    }
    sign("post", url+"/inbox", headers, json.dumps(accept), instance_user)
    async with HttpClient().post(url+"/inbox", data=json.dumps(accept), headers = headers) as resp:
        if resp.status != 200:
            raise HTTPException(status_code=400, detail=f"Received {resp.status} upon accepting")
        return

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

@router.post("/setup/{initkey}/")
async def setup_execute(request: Request, initkey : str,
                email:str=Body(),
                instancename:str=Body(),
                username:str=Body(),
                password:str=Body(),
                coordinates: Coordinates = Body(),
                perimeter: int = Body(),
    ):

    instance_settings = await InstanceSettingsSchema.retrieve()

    if instance_settings["initialization_key"] != initkey:
        raise HTTPException(status_code=403, detail="Not the corrent initialization key :(")

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
        "active": True,
        "admin": True,
        "moderator": True,
        "avatar":None,
        "role":"User"
    }

    new_user = await UserSchema.add(new_user)

    instance_user = {
        "email":"",
        "name":"instance",
        "pwhash":"",
        "active": False,
        "admin": False,
        "moderator": False,
        "avatar":None,
        "role":"User"
    }

    instance_user = await UserSchema.add(instance_user)

    instance_settings["name"] = instancename
    instance_settings["initialized"] = True
    instance_settings["initialization_key"] = ""
    instance_settings["perimeter"] = perimeter
    instance_settings["coordinates"] = coordinates

    await InstanceSettingsSchema.set(instance_settings)

    return {"ok": True}

