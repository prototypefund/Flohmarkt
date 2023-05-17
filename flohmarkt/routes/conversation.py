import uuid
import datetime

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.routes.activitypub import post_message_remote
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

async def convert_to_activitypub_message(msg, current_user, parent=None, item=None):
    hostname = cfg["General"]["ExternalURL"]
    item_user = await UserSchema.retrieve_single_id(item["user"])

    if parent["type"] != "item":
        username = current_user["name"]
        update = {
            "inReplyTo": parent['id'],
            "to": [
                parent["attributedTo"]
            ],
            "tag":[
                {
                    "type": "Mention",
                    "href": parent["attributedTo"],
                    "name": "@derpy@testcontainer.lan"
                }
            ]
        }
    else:
        if "@" in item_user['name']:
            username, remote_hostname = item_user['name'].split("@")
            remote_hostname = "https://"+remote_hostname
        else:
            username = item_user['name']
            remote_hostname = hostname
        update = {
            "inReplyTo": f"{remote_hostname}/users/{username}/items/{item['id']}",
            "to": [
                f"{remote_hostname}/users/{username}"
            ],
            "tag":[
                {
                    "type": "Mention",
                    "href": f"{remote_hostname}/users/{item_user['name']}",
                    "name": f"{item_user['name']}"
                }
            ]
        }

    date = datetime.datetime.now(tz=datetime.timezone.utc).isoformat().split(".")[0]+"Z"
    message_uuid = str(uuid.uuid4())

    ret = {
        "id": f"{hostname}/users/{username}/statuses/{message_uuid}",
        "type": "Note",
        "summary": None,
        "published": date,
        "url": f"{hostname}/~{item_user['name']}/{item['id']}#{message_uuid}",
        "attributedTo": f"{hostname}/users/{current_user['name']}",
        "cc": [],
        "sensitive": False,
        "conversation": "tag:mastodo.lan,2023-03-29:objectId=27:objectType=Conversation",
        "content": "<p>"+msg["text"]+"</p>",
        "contentMap": {
            "en": "<p>"+msg["text"]+"</p>"
        },
        "attachment": [],
        "replies": {
            "id": f"{hostname}/users/{item_user['name']}/statuses/{message_uuid}/replies",
            "type": "Collection",
            "first": {
                "type": "CollectionPage",
                "next": f"{hostname}/users/{item_user['name']}/statuses/{message_uuid}/replies?only_other_accounts=true&page=true",
                "partOf": f"{hostname}/users/{item_user['name']}/statuses/{message_uuid}/replies",
                "items": []
            }
        }
    }
    ret.update(update)
    return ret

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
        message = await convert_to_activitypub_message(msg, current_user,parent=last_message, item=item)
    else:
        if item["user"] != current_user["id"]:
            message = await convert_to_activitypub_message(msg, current_user, parent=item, item=item)
        else:
            raise HTTPException(status_code=403, detail="You may not answer your own items")

    conversation["messages"].append(message)
    await ConversationSchema.update(conversation['id'], conversation)

    await post_message_remote(message, current_user)

@router.delete("/{ident}", response_description="deleted")
async def delete_user(ident: str):
    await UserSchema.delete(ident)
    return "SUS"
