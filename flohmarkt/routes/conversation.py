from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.models.item import ItemSchema
from flohmarkt.models.user import UserSchema
from flohmarkt.models.conversation import ConversationSchema, MessageSchema
from flohmarkt.auth import oauth2, get_current_user

router = APIRouter()


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

async def convert_to_activitypub_message(msg, current_user, last_message=None, item=None):
    if last_message is not None and item is not None:
        raise Exception("Please suppley either last_message or item, not both")
    if last_message is None and item is None:
        raise Exception("Please suppley either last_message or item")

    hostname = cfg["General"]["ExternalURL"]

    if last_message is not None:
        update = {
            "inReplyTo": last_message['id'],
            "to": [
                last_message["attributedTo"]
            ],
            "tag":[
                {
                    "type": "Mention",
                    "href": last_message["attributedTo"],
                    "name": "@derpy@testcontainer.lan"
                }
            ]
        }
    if item is not None:
        item_user = await UserSchema.retrieve_single_id(item["user"])
        update = {
            "inReplyTo": f"{hostname}/users/{current_user['name']}/items/{item['id']}",
            "to": [
                f"{hostname}/users/{item_user['name']}"
            ],
            "tag":[
                {
                    "type": "Mention",
                    "href": f"{hostname}/users/{item_user['name']}",
                    "name": "@derpy@testcontainer.lan"
                }
            ]
        }

    ret = {
        "id": f"{hostname}/users/{current_user['name']}/statuses/110113452826075130",
        "type": "Note",
        "summary": None,
        "published": "2023-03-30T17:39:09Z",
        "url": "https://mastodo.lan/@grindhold/110113452826075130#",
        "attributedTo": "https://mastodo.lan/users/grindhold",
        "cc": [],
        "sensitive": False,
        "conversation": "tag:mastodo.lan,2023-03-29:objectId=27:objectType=Conversation",
        "content": "<p>"+msg["text"]+"</p>",
        "contentMap": {
            "en": "<p>"+msg["text"]+"</p>"
        },
        "attachment": [],
        "replies": {
            "id": "https://mastodo.lan/users/grindhold/statuses/110113452826075130/replies",
            "type": "Collection",
            "first": {
                "type": "CollectionPage",
                "next": "https://mastodo.lan/users/grindhold/statuses/110113452826075130/replies?only_other_accounts=true&page=true",
                "partOf": "https://mastodo.lan/users/grindhold/statuses/110113452826075130/replies",
                "items": []
            }
        }
    }
    ret.update(update)
    return ret

async def get_last_message(conversation, current_user):
    hostname = cfg["General"]["ExternalURL"]
    current_actor = f"{hostname}/users/{current_user['name']}",
    if not "messages" in conversation:
        return None
    for i in range(len(conversation["messages"])):
        idx = len(conversation["messages"])-1-i
        if conversation["messages"][idx]["attributedTo"] != current_actor:
            return conversation["messages"][idx]
    return None

@router.post("/to_item/{item_id}", response_description="Update stuff")
async def create_message(item_id: str, msg: dict = Body(...), current_user: UserSchema = Depends(get_current_user)):
    hostname = cfg["General"]["ExternalURL"]
    actor = f"{hostname}/users/{current_user['name']}"
    item = await ItemSchema.retrieve_single_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item is not here :(")
    conversation = await ConversationSchema.retrieve_for_id(msg["conversation_id"])
    if conversation is None:
        print(actor)
        conversation = {
            "user_id" : item['user'],
            "remote_user" : actor,
            "item_id" : item['id'],
            "messages" : []
        }
        conversation = await ConversationSchema.add(conversation)
    
    last_message = await get_last_message(conversation, current_user)
    if last_message is not None:
        conversation["messages"].append(await convert_to_activitypub_message(msg, current_user,last_message=last_message))
        await ConversationSchema.update(conversation['id'], conversation)
    else:
        if item["user"] != current_user["id"]:
            conversation["messages"].append(await convert_to_activitypub_message(msg, current_user, item=item))
            await ConversationSchema.update(conversation['id'], conversation)



@router.delete("/{ident}", response_description="deleted")
async def delete_user(ident: str):
    await UserSchema.delete(ident)
    return "SUS"
