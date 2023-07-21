import asyncio
from typing import List

from fastapi import APIRouter, Body, Depends, Request, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from flohmarkt.config import cfg
from flohmarkt.ratelimit import limiter
from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema, UpdateItemModel
from flohmarkt.models.conversation import ConversationSchema
from flohmarkt.auth import get_current_user
from flohmarkt.routes.activitypub import post_item_to_remote, delete_item_remote, post_message_remote,convert_to_activitypub_message, replicate_item
from flohmarkt.routes.conversation import get_last_message

router = APIRouter()

@router.post("/", response_description="Added")
@limiter.limit("6/minute")
async def add_item(request: Request, item: ItemSchema = Body(...), 
                   current_user: UserSchema = Depends(get_current_user)):
    item = jsonable_encoder(item)
    item["user"] = current_user["id"]
    new_item = await ItemSchema.add(item, current_user)
    await post_item_to_remote(new_item, current_user)
    return new_item

@router.get("/", response_description="All items")
async def get_items():
    items = await ItemSchema.retrieve()
    return items

@router.get("/many", response_description="list of watched items")
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
async def update_item(ident: str, req: UpdateItemModel = Body(...)):
    req = {k: v for k,v in req.dict().items() if v is not None}
    updated_item = await ItemSchema.update(ident, req)
    if updated_item:
        return "YEEEH"
    return "NOOO"

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

@router.post("/{ident}/give")
async def give_item(ident: str, msg: dict = Body(...), current_user: UserSchema = Depends(get_current_user)):
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
    for convo in conversations:
        if conversation_with_target == convo:
            msg["text"] = final_message
        else:
            msg["text"] = denied_message

        last_message = await get_last_message(convo, current_user)
        message = await convert_to_activitypub_message(msg, current_user,parent=last_message, item=item)
        convo["messages"].append(message)
        await ConversationSchema.update(convo['id'], convo)
        tasks.append(post_message_remote(message, current_user))

    await asyncio.gather(*tasks)

@router.delete("/{ident}", response_description="Marked Item for subsequent deletion")
async def delete_item(ident: str, current_user: UserSchema = Depends(get_current_user)):
    item = await ItemSchema.retrieve_single_id(ident)

    if item["user"] != current_user["id"]:
        if not current_user["admin"] and not current_user["moderator"]:
            raise HTTPException(status_code=403, detail="Only owners, admins or moderators may delete item")

    await ItemSchema.delete(ident)
    await delete_item_remote(item, current_user)
    return Response(content="", status_code=204)
