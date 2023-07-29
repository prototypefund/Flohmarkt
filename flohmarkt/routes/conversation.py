import uuid

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.routes.activitypub import post_message_remote, convert_to_activitypub_message
from flohmarkt.models.item import ItemSchema
from flohmarkt.models.user import UserSchema
from flohmarkt.models.conversation import ConversationSchema, MessageSchema
from flohmarkt.auth import oauth2, get_current_user

router = APIRouter()

@router.get("/own")
async def _(req : Request, skip: int = 0,  current_user: UserSchema = Depends(get_current_user)):
    return await ConversationSchema.retrieve_by_user(current_user, skip)

@router.get("/by_item/{item_id}", response_description="Get all conversation objects belonging to an item")
async def _(item_id:str, current_user: UserSchema = Depends(get_current_user)):
    hostname = cfg["General"]["ExternalURL"]

    item = await ItemSchema.retrieve_single_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item is not here :(")

 
    conversations = await ConversationSchema.retrieve_for_item(item['id'])

    if item["user"] != current_user["id"]:
        conversations = [
            c for c in conversations if c["remote_user"] == f"{hostname}/users/{current_user['name']}"
        ]

    return conversations

async def get_last_message(conversation, current_user):
    hostname = cfg["General"]["ExternalURL"]
    current_actor = f"{hostname}/users/{current_user['name']}"
    if not "messages" in conversation:
        return None
    for i in range(len(conversation["messages"])):
        idx = len(conversation["messages"])-1-i
        if conversation["messages"][idx]["attributedTo"] != current_actor:
            return conversation["messages"][idx]
    return None

@router.post("/to_item/{item_id}", response_description="Update stuff")
async def create_message(item_id: str, msg: dict = Body(...), current_user: UserSchema = Depends(get_current_user)):
    if current_user["banned"]:
        raise HTTPException(status_code=403, detail="You are banned")

    hostname = cfg["General"]["ExternalURL"]
    actor = f"{hostname}/users/{current_user['name']}"
    item = await ItemSchema.retrieve_single_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item is not here :(")

    if msg["text"] == "":
        raise HTTPException(status_code=400, detail="Please provide text :(")

    conversation = await ConversationSchema.retrieve_for_id(msg["conversation_id"])

    if conversation is None:
        conversation = await ConversationSchema.retrieve_for_item_remote_user(msg["item_id"], actor)

    if conversation is None:
        conversation = {
            "user_id" : item['user'],
            "remote_user" : actor,
            "item_id" : item['id'],
            "messages" : []
        }
        conversation = await ConversationSchema.add(conversation)
    
    last_message = await get_last_message(conversation, current_user)
    if last_message is not None:
        message = await convert_to_activitypub_message(msg, current_user,parent=last_message, item=item)
    else:
        if item["user"] != current_user["id"]:
            message = await convert_to_activitypub_message(msg, current_user, parent=item, item=item)
        else:
            raise HTTPException(status_code=403, detail="You may not answer your own items")

    conversation["messages"].append(message)
    await ConversationSchema.update(conversation['id'], conversation)

    await post_message_remote(message, current_user)

    return conversation

@router.delete("/{ident}", response_description="deleted")
async def delete_user(ident: str):
    await UserSchema.delete(ident)
    return "SUS"
