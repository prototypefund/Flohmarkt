from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema, UpdateUserModel
from flohmarkt.models.item import ItemSchema
from flohmarkt.auth import oauth2, get_current_user, get_optional_current_user
from flohmarkt.http import HttpClient

router = APIRouter()

@router.get("/", response_description="All users")
async def get_users(skip: int = 0, current_user : UserSchema = Depends(get_current_user)):
    if not (current_user["admin"] or current_user["moderator"]):
        raise HTTPException(status_code=403, detail="Only admins/mods :(")
    users = await UserSchema.retrieve_local(skip)
    for user in users:
        await UserSchema.filter(user, current_user)
    return users

@router.get("/{ident}", response_description="A single user if any")
async def get_user(ident:str,current_user : UserSchema = Depends(get_optional_current_user)):
    user = await UserSchema.retrieve_single_id(ident)
    if user is None:
        raise HTTPException(status_code=404, detail="User is not here :(")
    await UserSchema.filter(user, current_user)
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
async def delete_user(ident: str, current_user : UserSchema = Depends(get_current_user)):
    if ident != current_user["id"]:
        if not current_user["admin"] and not current_user["moderator"]:
            raise HTTPException(status_code=403, detail="Only owners, admins or moderators may delete item")
    else:
        if current_user["admin"]:
            raise HTTPException(status_code=400, detail="Admins cant delete themselves. Resign first!")


    items = await ItemSchema.retrieve_by_user(ident)
    for item in items:
        await ItemSchema.delete(item["id"])

    await UserSchema.delete(ident)
    return 

@router.get("/{ident}/ban", response_description="deleted")
async def delete_user(ident: str, current_user : UserSchema = Depends(get_current_user)):
    if not (current_user["admin"] or current_user["moderator"]):
        raise HTTPException(status_code=403, detail="Only admins/mods :(")
    
    user = await UserSchema.retrieve_single_id(ident)
    if user is None:
        raise HTTPException(status_code=404, detail="User not here :(")

    user["banned"] = True

    if await UserSchema.update(ident, user):    
        return user
    else:
        raise HTTPException(status_code=500, detail="Something went wrong while updating")
    
@router.get("/{ident}/unban", response_description="deleted")
async def delete_user(ident: str, current_user : UserSchema = Depends(get_current_user)):
    if not (current_user["admin"] or current_user["moderator"]):
        raise HTTPException(status_code=403, detail="Only admins/mods :(")
    
    user = await UserSchema.retrieve_single_id(ident)
    if user is None:
        raise HTTPException(status_code=404, detail="User not here :(")

    user["banned"] = False

    if await UserSchema.update(ident, user):    
        return user
    else:
        raise HTTPException(status_code=500, detail="Something went wrong while updating")

@router.get("/{ident}/mark_read", response_description="deleted")
async def delete_user(ident: str, current_user : UserSchema = Depends(get_current_user)):
    if current_user["id"] != ident:
        raise HTTPException(status_code=403, detail="You can only modify your own state :(")

    user = await UserSchema.retrieve_single_id(ident)
    if user is None:
        raise HTTPException(status_code=404, detail="User not here :(")

    user["has_unread"] = False

    if await UserSchema.update(ident, user):    
        return user
    else:
        raise HTTPException(status_code=500, detail="Something went wrong while updating")

@router.get("/{ident}/block_user", response_description="current list of blocked instances")
async def block_instance(user : str, block: bool, current_user: UserSchema = Depends(get_current_user)):
    blocked_users = current_user.get("blocked_users",[])

    if block:
        actor = ""
        name, host = user.split("@")
        name = name.lstrip("@") # for mastodon
        webfinger_url = "https://"+host+"/.well-known/webfinger?resource=acct:"+user
        async with HttpClient().get(webfinger_url) as r:
            json = await r.json()
            print(json)
            if not "links" in json:
                raise HTTPException(status_code=403, detail="Remote instance does not supply actorurl")
            found = False
            for link in json['links']:
                if link["rel"] == "self":
                    actor = link["href"]
                    found = True
                    break
            if not found:
                raise HTTPException(status_code=403, detail="Remote instance doesn't supply actorurl")
        if actor not in blocked_users:
            blocked_users.append(actor)
    else:
        if user in blocked_users:
            blocked_users.remove(user)

    current_user["blocked_users"] = blocked_users

    await UserSchema.update(current_user["id"], current_user)

    return blocked_users
