import asyncio

from fastapi import APIRouter, Body, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response

from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema, UpdateItemModel
from flohmarkt.models.conversation import ConversationSchema
from flohmarkt.auth import get_current_user
from flohmarkt.routes.activitypub import post_item_to_remote, delete_item_remote, post_message_remote
from flohmarkt.routes.conversation import get_last_message, convert_to_activitypub_message

router = APIRouter()

@router.post("/", response_description="Added")
async def add_item(request: Request, item: ItemSchema = Body(...), 
                   current_user: UserSchema = Depends(get_current_user)):
    item = jsonable_encoder(item)
    item["user"] = current_user["id"]
    new_item = await ItemSchema.add(item)
    await post_item_to_remote(new_item, current_user)
    return new_item

@router.get("/", response_description="All items")
async def get_items():
    items = await ItemSchema.retrieve()
    return items

#TODO: implement
@router.get("/most_contested", response_description="All items")
async def get_items():
    #items = await ItemSchema.retrieve()
    #TODO: implement
    return []

@router.get("/newest", response_description="Newest items")
async def get_items():
    return await ItemSchema.retrieve_newest()

@router.get("/search/{searchterm}", response_description="Search results")
async def get_items(searchterm: str):
    return await ItemSchema.search(searchterm)

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
