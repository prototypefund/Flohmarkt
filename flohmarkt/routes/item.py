import asyncio
import difflib
from typing import List

from fastapi import APIRouter, Body, Depends, Request, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from flohmarkt.config import cfg
from flohmarkt.ratelimit import limiter
from flohmarkt.socketpool import Socketpool
from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema, UpdateItemModel
from flohmarkt.models.conversation import ConversationSchema
from flohmarkt.auth import get_current_user
from flohmarkt.routes.activitypub import post_item_to_remote, delete_item_remote, post_message_remote,convert_to_activitypub_message, replicate_item
from flohmarkt.routes.conversation import get_last_message

router = APIRouter()

@router.post("/", response_description="Added")
#@limiter.limit("6/minute")
async def add_item(request: Request, item: ItemSchema = Body(...), 
                   current_user: UserSchema = Depends(get_current_user)):
    if current_user.get("banned",False):
        raise HTTPException(status_code=403, detail="You are banned")
    item = jsonable_encoder(item)
    item["user"] = current_user["id"]
    new_item = await ItemSchema.add(item, current_user)
    await post_item_to_remote(new_item, current_user)
    return new_item

@router.get("/", response_description="All items")
async def get_items():
    items = await ItemSchema.retrieve()
    return items

@router.get("/many", response_description="list of many items")
async def get_many_items(req : Request, item : List[str] = Query(), current_user : UserSchema = Depends(get_current_user)):
    return await ItemSchema.retrieve_many(item)

@router.get("/get_watched", response_description="list of watched items")
async def get_watched_items(req : Request, current_user : UserSchema = Depends(get_current_user)):
    if "watching" in current_user:
        return await ItemSchema.retrieve_many(current_user["watching"])
    else:
        return []

@router.get("/most_contested", response_description="All items")
async def get_items():
    return await ItemSchema.retrieve_most_contested()

@router.get("/newest", response_description="Newest items")
async def get_items():
    return await ItemSchema.retrieve_newest()

@router.get("/search", response_description="Search results")
#@limiter.limit("6/minute") # limit needed to avoid enabling DDOS other services via fetch_remote_item
async def get_items(req: Request, q: str, skip: int = 0):
    searchterm = q
    if searchterm.startswith(("http://","https://")):
        ident = searchterm.split("/")[-1]
        item = await ItemSchema.retrieve_single_id(ident)
        if item is not None:
            return [ item ]
        if not searchterm.startswith(cfg["General"]["ExternalURL"]):
            item = await replicate_item(searchterm)
        else:
            item = None
        return [ item ] if item is not None else []
    else:
        return await ItemSchema.search(searchterm, skip)

@router.get("/oldest", response_description="Oldest items")
async def get_items():
    return await ItemSchema.retrieve_oldest()

@router.get("/by_user/{user_id}", response_description="All items of user")
async def get_single_item(user_id: str):
    return await ItemSchema.retrieve_by_user(user_id)

@router.get("/{ident}", response_description="A single item if any")
async def get_item(ident:str):
    item = await ItemSchema.retrieve_single_id(ident)
    return item

@router.put("/{ident}", response_description="Update stuff")
async def update_item(ident: str, req: UpdateItemModel = Body(...), current_user: UserSchema = Depends(get_current_user)):
    data = jsonable_encoder(req)

    olditem = await ItemSchema.retrieve_single_id(ident)

    updated_item = await ItemSchema.update(ident, data)

    newitem = await ItemSchema.retrieve_single_id(ident)
    if updated_item:

        diff = difflib.Differ()
        diffresult = diff.compare(
            olditem["description"].splitlines(True),
            newitem["description"].splitlines(True)
        ) 

        conversations = await ConversationSchema.retrieve_for_item(newitem["id"])

        fulldiff = "The owner has changed the item description:<br><br><pre>"
        for diffline in diffresult:
            if not diffline.startswith(("+","-")):
                continue
            fulldiff += diffline+"\n"

        fulldiff += "</pre>"
        
        tasks = []
        for convo in conversations:
            msg = {"text": fulldiff}

            last_message = await get_last_message(convo, current_user)
            message = await convert_to_activitypub_message(msg, current_user,parent=last_message, item=newitem)
            convo["messages"].append(message)
            await ConversationSchema.update(convo['id'], convo)

            if message["actor"] == convo["remote_user"]:
                receiver = await UserSchema.retrieve_single_id(convo["user_id"])
            else:
                receiver = await UserSchema.retrieve_single_remote_url(convo["remote_user"])
            if receiver is not None:
                receiver["has_unread"] = True
                await UserSchema.update(receiver["id"], receiver)

            tasks.append(post_message_remote(message, current_user))
            tasks.append(Socketpool.send_message(message))

        await asyncio.gather(*tasks)
        
        
        return {}

    raise HTTPException(status_code=500, detail="something went wrong when updating")

@router.get("/{ident}/watch")
async def watch_item(ident: str, current_user: UserSchema = Depends(get_current_user)):
    item = await ItemSchema.retrieve_single_id(ident)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not here :(")

    if not "watching" in current_user:
        current_user["watching"] = []

    if not ident in current_user["watching"]:
        current_user["watching"].append(ident)
        await UserSchema.update(current_user["id"], current_user)

    return {}

@router.get("/{ident}/unwatch")
async def unwatch_item(ident: str, current_user: UserSchema = Depends(get_current_user)):
    item = await ItemSchema.retrieve_single_id(ident)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not here :(")

    if not "watching" in current_user:
        current_user["watching"] = []

    if ident in current_user["watching"]:
        current_user["watching"].remove(ident)
        await UserSchema.update(current_user["id"], current_user)

    return {}

@router.get("/{ident}/suspend")
async def unwatch_item(ident: str, current_user: UserSchema = Depends(get_current_user)):
    if not (current_user["admin"] or current_user["moderator"]):
        raise HTTPException(status_code=403, detail="Only admins/mods :(")

    item = await ItemSchema.retrieve_single_id(ident)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not here :(")

    item["suspended"] = True

    res = await ItemSchema.update(item["id"], item)

    if res:
        return item
    else:
        raise HTTPException(status_code=500, detail="something went wrong updating")

@router.get("/{ident}/unsuspend")
async def unwatch_item(ident: str, current_user: UserSchema = Depends(get_current_user)):
    if not (current_user["admin"] or current_user["moderator"]):
        raise HTTPException(status_code=403, detail="Only admins/mods :(")

    item = await ItemSchema.retrieve_single_id(ident)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not here :(")

    item["suspended"] = False
    res = await ItemSchema.update(item["id"], item)

    if res:
        return item
    else:
        raise HTTPException(status_code=500, detail="something went wrong updating")

@router.post("/{ident}/give")
async def give_item(ident: str, msg: dict = Body(...), current_user: UserSchema = Depends(get_current_user)):
    if current_user.get("banned",False):
        raise HTTPException(status_code=403, detail="You are banned")

    item = await ItemSchema.retrieve_single_id(ident)

    item["closed"] = True

    await ItemSchema.update(item["id"], item)

    if item["user"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only owners may give item to a user")

    conversations = await ConversationSchema.retrieve_for_item(item["id"])
    conversation_with_target = await ConversationSchema.retrieve_for_id(msg["conversation_id"])

    final_message = msg["text"]
    denied_message = "This item has found a new home with another user."

    tasks = []

    assign_convo = None
    for convo in conversations:
        if conversation_with_target == convo:
            msg["text"] = final_message
        else:
            msg["text"] = denied_message

        last_message = await get_last_message(convo, current_user)

        print(msg, current_user, last_message, item)

        message = await convert_to_activitypub_message(msg, current_user,parent=last_message, item=item)
        if conversation_with_target == convo:
            assign_convo = convo
        convo["messages"].append(message)
        await ConversationSchema.update(convo['id'], convo)

        print(message)

        if message["actor"] == convo["remote_user"]:
            receiver = await UserSchema.retrieve_single_id(convo["user_id"])
        else:
            receiver = await UserSchema.retrieve_single_remote_url(convo["remote_user"])
        if receiver is not None:
            receiver["has_unread"] = True
            await UserSchema.update(receiver["id"], receiver)

        tasks.append(post_message_remote(message, current_user))
        tasks.append(Socketpool.send_message(message))

    await asyncio.gather(*tasks)
    return assign_convo

@router.delete("/{ident}", response_description="Marked Item for subsequent deletion")
async def delete_item(ident: str, current_user: UserSchema = Depends(get_current_user)):
    item = await ItemSchema.retrieve_single_id(ident)

    if item["user"] != current_user["id"]:
        if not current_user["admin"] and not current_user["moderator"]:
            raise HTTPException(status_code=403, detail="Only owners, admins or moderators may delete item")

    await ItemSchema.delete(ident)
    await delete_item_remote(item, current_user)
    return Response(content="", status_code=204)
