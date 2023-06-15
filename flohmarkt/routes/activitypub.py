import json
import asyncio
import re
import os
import uuid

from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from typing import List

from flohmarkt.config import cfg
from flohmarkt.signatures import verify, sign
from flohmarkt.http import HttpClient
from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema
from flohmarkt.models.instance_settings import InstanceSettingsSchema
from flohmarkt.models.conversation import ConversationSchema
from flohmarkt.models.follow import AcceptSchema

router = APIRouter()
uuid_regex = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)

async def get_userinfo(actor : str) -> dict:
    async with HttpClient().get(actor, headers = {
            "Accept":"application/json"
        }) as resp:
        return await resp.json()

async def accept(rcv_inbox, follow, user):
    hostname = cfg["General"]["ExternalURL"]
    accept = AcceptSchema(
        object=follow,
        id = f"{hostname}/users/{user['name']}#accepts/follows/42",
        type = "Accept",
        actor = f"{hostname}/users/{user['name']}",
        context = "https://www.w3.org/ns/activitystreams"
    )
    #TODO determine numbers
    accept = jsonable_encoder(accept)
    headers = {
        "Content-Type":"application/json"
    }
    sign("post", rcv_inbox, headers, json.dumps(accept), user)
    async with HttpClient().post(rcv_inbox, data=json.dumps(accept), headers = headers) as resp:
        if resp.status != 200:
            raise HTTPException(status_code=400, detail=f"Received {resp.status} upon accepting")
        return

async def follow(obj):
    name = obj['object'].replace(cfg["General"]["ExternalURL"]+"/users/","",1)
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")
    if "followers" not in user:
        user["followers"] = {}
    user["followers"][obj['id']] = obj

    await UserSchema.update(user['id'], user)

    userinfo = await get_userinfo(obj['actor'])
    await accept(userinfo['inbox'], obj, user)

    return {}

async def unfollow(obj):
    name = obj['object']['object'].replace(cfg["General"]["ExternalURL"]+"/users/","",1)
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")
    if "followers" in user:
        try:
            del(user["followers"][obj['object']['id']])
        except KeyError as e:
            return HTTPException(status_code=404, detail="object does not exist")
        await UserSchema.update(user['id'], user, replace=True)
    return {}

async def replicate_image(image_url : str) -> str:
    ident = image_url.split("/")[-1]
    if not uuid_regex.match (ident):
        ident = str(uuid.uuid4())

    imagepath = os.path.join(cfg["General"]["ImagePath"], ident+".jpg")

    async with HttpClient().get(image_url, headers = {
            "Accept":"image/jpeg"
        }) as resp:
        imagefile = open(imagepath, "wb")
        imagefile.write(await resp.read())
        imagefile.close()
        return ident

async def replicate_user(user_url: str) -> str:
    ident = user_url.split("/")[-1]
    if not uuid_regex.match (ident):
        ident = str(uuid.uuid4())

    async with HttpClient().get(user_url, headers = {
            "Accept":"application/json"
        }) as resp:
        userinfo = await resp.json()
        parsed = urlparse(user_url)

        username = userinfo["preferredUsername"]+"@"+parsed.netloc

        user = await UserSchema.retrieve_single_name(username)
        if user is not None:
            return user

        avatar = None
        if "icon" in userinfo:
            async with HttpClient().get(userinfo["icon"]["url"]) as resp:
                image = await resp.read()

                avatar = str(uuid.uuid4())

                imagefile = open(os.path.join(cfg["General"]["ImagePath"], avatar+".jpg"), "wb")
                imagefile.write(image)
                imagefile.close()

        new_user = {
            "id": ident,
            "name": username,
            "pwhash": "-",
            "admin": False,
            "moderator": False,
            "active": False,
            "activation_code": "-",
            "avatar":avatar,
            "remote_url": user_url,
        }
        await UserSchema.add(new_user)
        return new_user

async def create_new_item(req: Request, msg: dict):
    hostname = cfg["General"]["ExternalURL"]

    tasks = []
    for attachment in msg["object"]["attachment"]:
        tasks.append(replicate_image(attachment["url"]))
    image_urls = await asyncio.gather(*tasks)

    new_user = await replicate_user(msg["actor"])

    ident = msg["object"]["flohmarkt:data"]["original_id"]
    item = await ItemSchema.retrieve_single_id(ident)
    if item is not None:
        raise Exception(f"Not allowed to override existing item: Double ID {ident}")

    item = {
        "id": ident,
        "type":"item",
        "name":msg["object"]["flohmarkt:data"]["name"],
        "description":msg["object"]["flohmarkt:data"]["description"],
        "price":msg["object"]["flohmarkt:data"]["price"],
        "creation_date ": msg["object"]["published"],
        "user": new_user["id"],
        "images": image_urls
    }
    await ItemSchema.add(item)

    return Response(content="0", status_code=202)

async def inbox_process_create(req: Request, msg: dict):
    hostname = cfg["General"]["ExternalURL"]
    if msg["id"].startswith(hostname):
        raise HTTPException(status_code=302, detail="Already exists")

    if "https://www.w3.org/ns/activitystreams#Public" in msg["to"]:
        if "object" in msg and "inReplyTo" in msg["object"] and msg["object"]["inReplyTo"] is not None:
            pass # print("not allowed to post publicly to item")
        else:
            return await create_new_item(req, msg)

    if len(msg["to"]) != 1:
        raise HTTPException(status_code=400, detail="Can only accept private messages to 1 user")

    username = msg["to"][0].replace(f"{hostname}/users/","")
    user = await UserSchema.retrieve_single_name(username)

    if user is None:
        raise HTTPException(status_code=404, detail="Targeted user not found")

    if f"{hostname}/users/{username}/items/" in msg["object"]["inReplyTo"]:
        item_id = msg["object"]["inReplyTo"].replace(
            f"{hostname}/users/{username}/items/", ""
        )
        item = await ItemSchema.retrieve_single_id(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Targeted item not found")
        conversation = await ConversationSchema.retrieve_for_item_remote_user(item_id, msg["actor"])
    else:
        conversation = await ConversationSchema.retrieve_for_message_id(msg["object"]["inReplyTo"])

    if conversation is None:
        conversation = {
            "user_id" : user['id'],
            "remote_user" : msg["actor"],
            "item_id" : item['id'],
            "messages" : []
        }
        conversation = await ConversationSchema.add(conversation)

    conversation["messages"].append(msg["object"])

    await ConversationSchema.update(conversation['id'], conversation)

    return Response(content="0", status_code=202)

async def inbox_process_update(req: Request, msg: dict):
    hostname = cfg["General"]["ExternalURL"]
    if msg["id"].startswith(hostname):
        raise HTTPException(status_code=302, detail="Already exists")

    if len(msg["to"]) != 1:
        raise HTTPException(status_code=400, detail="Can only accept private messages to 1 user")

    username = msg["to"][0].replace(f"{hostname}/users/","")
    user = await UserSchema.retrieve_single_name(username)

    if user is None:
        raise HTTPException(status_code=404, detail="Targeted user not found")

    if f"{hostname}/users/{username}/items/" in msg["object"]["inReplyTo"]:
        item_id = msg["object"]["inReplyTo"].replace(
            f"{hostname}/users/{username}/items/", ""
        )
        item = await ItemSchema.retrieve_single_id(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail="Targeted item not found")
        conversation = await ConversationSchema.retrieve_for_item_remote_user(item_id, msg["actor"])
    else:
        conversation = await ConversationSchema.retrieve_for_message_id(msg["object"]["inReplyTo"])

    if conversation is None:
        raise HTTPException(status_code=404, detail="Trying to update a non-existing conversation")

    found = False
    for message in conversation["messages"]:
        if message["id"] == msg["object"]["id"]:
            message["overridden"] = found = True

    if not found:
        raise HTTPException(status_code=404, detail="Trying to update a non-existing message")

    conversation["messages"].append(msg["object"])

    await ConversationSchema.update(conversation['id'], conversation)

    return Response(content="0", status_code=202)

async def inbox_process_delete(req: Request, msg: dict):
    parsed_actor = urlparse(msg["actor"])
    item_id = msg["object"]["id"].split("/")[-1]
    item = await ItemSchema.retrieve_single_id(item_id)

    if item is not None:
        # Try to delete item
        username = parsed_actor.path.split("/")[-1]+"@"+parsed_actor.netloc
        user = await UserSchema.retrieve_single_name(username)

        if user["id"] != item["user"]:
            raise HTTPException(status_code=403, detail="Not allowed to delete other users items")

        await ItemSchema.delete(item["id"])
        return Response(content="", status_code=204)
    else:
        # Try to determine message
        conv = await ConversationSchema.retrieve_for_message_id(msg["object"]["id"])
        for message in conv["messages"]:
            if message["id"] == msg["object"]["id"]:
                message["overridden"] = True

        await ConversationSchema.update(conv['id'], conv)

    
async def inbox_process_follow(req : Request, msg: dict):
    """
    this is where instance follows are being handled
    """
    hostname = cfg["General"]["ExternalURL"]
    instance = msg["actor"].replace(f"/users/instance","")
    instance_settings = await InstanceSettingsSchema.retrieve()
    if instance not in instance_settings["pending_followers"]:
        instance_settings["pending_followers"].append(instance)

    await InstanceSettingsSchema.set(instance_settings)

    return Response(content="0", status_code=202)


async def inbox_process_accept(req : Request, msg: dict):
    hostname = cfg["General"]["ExternalURL"]
    instance = msg["actor"].replace(f"/users/instance","",1)
    instance_settings = await InstanceSettingsSchema.retrieve()
    if instance not in instance_settings["pending_following"]:
        raise HTTPException(status_code=404, detail="we are not waiting for this instance follow")

    instance_settings["pending_following"].remove(instance)

    if instance not in instance_settings["following"]:
        instance_settings["following"].append(instance)

    instance_settings = await InstanceSettingsSchema.set(instance_settings)
    return Response(content="0", status_code=202)

async def inbox_process_reject(req : Request, msg: dict):
    hostname = cfg["General"]["ExternalURL"]
    instance = msg["actor"].replace(f"/users/instance","",1)
    instance_settings = await InstanceSettingsSchema.retrieve()
    if instance not in instance_settings["pending_following"]:
        raise HTTPException(status_code=404, detail="we are not waiting for this instance follow")

    instance_settings["pending_following"].remove(instance)

    instance_settings = await InstanceSettingsSchema.set(instance_settings)
    return Response(content="0", status_code=204)



@router.post("/inbox")
async def inbox(req : Request, msg : dict = Body(...) ):
    if not await verify(req):
        raise HTTPException(status_code=401, detail="request signature could not be validated")

    if msg["type"] == "Create":
        return await inbox_process_create(req, msg)
    elif msg["type"] == "Update":
        return await inbox_process_update(req, msg)
    elif msg["type"] == "Delete":
        return await inbox_process_delete(req, msg)
    elif msg["type"] == "Follow":
        return await inbox_process_follow(req, msg)
    elif msg["type"] == "Accept":
        return await inbox_process_accept(req, msg)
    elif msg["type"] == "Reject":
        return await inbox_process_reject(req, msg)


@router.get("/users/{name}/followers")
async def followers(name: str, page : int = None):
    hostname = cfg["General"]["ExternalURL"]
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")

    if page is None:
        return {
            "@context":"https://www.w3.org/ns/activitystreams",
            "id":f"{hostname}/users/{user['name']}/followers",
            "type":"OrderedCollection",
            "totalItems":len(user.get("followers",[])),
            "first":f"{hostname}/users/{user['name']}/followers?page=1"
        }
    else:
        if page < 1:
            raise HTTPException(status_code=404, detail="Page not found :(")
        return {
            "@context":"https://www.w3.org/ns/activitystreams",
            "id":f"{hostname}/users/{user['name']}/followers?page=1",
            "type":"OrderedCollectionPage",
            "totalItems":len(user.get("followers",[])),
            "partOf":f"{hostname}/users/{user['name']}/followers",
            "orderedItems": [
                x["actor"] for x in list(user["followers"].values())[(page-1)*10:page*10]
            ]
        }



@router.get("/users/{name}/following")
async def following():
    return {}

@router.post("/users/{name}/inbox")
async def user_inbox(req: Request, name: str, msg : dict = Body(...) ):
    if not await verify(req):
        raise HTTPException(status_code=401, detail="request signature could not be validated")
    else:
        print("Valid signature")
    if msg['type'] == "Follow":
        result = await follow(msg)
        return Response(content="0", status_code=202)
    elif msg['type'] == "Undo":
        if msg['object']['type'] == "Follow":
            return await unfollow(msg)
    return {}

async def get_inbox_list_from_activity(data: dict):
    hostname=cfg["General"]["ExternalURL"]

    urls = []
    urls.extend(data.get("to", []))
    urls.extend(data.get("cc", []))

    hosts = {}

    if "https://www.w3.org/ns/activitystreams#Public" in urls:
        urls.remove("https://www.w3.org/ns/activitystreams#Public")

        instance_settings = await InstanceSettingsSchema.retrieve()
        urls.extend([i + "/inbox" for i in instance_settings["followers"]])
        
        username = data["actor"].replace(hostname+"/users/", "", 1)
        user = await UserSchema.retrieve_single_name(username)
        for follower in user.get("followers",{}).values():
            urls.append(follower["actor"])

    for url in urls:
        parsed = urlparse(url)
        inbox = f"{parsed.scheme}://{parsed.netloc}/inbox"
        hosts[inbox] = 1

    return list(hosts.keys())

async def delete_item_remote(item: ItemSchema, user: UserSchema):
    hostname = cfg["General"]["ExternalURL"]
    item = await item_to_delete_activity(item, user)
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            {
                "ostatus": "http://ostatus.org#",
                "atomUri": "ostatus:atomUri",
            },
        ]
    }
    data.update(item)

    headers = {
        "Content-Type":"application/json"
    }

    rcv_inboxes = await get_inbox_list_from_activity(data)

    tasks = []
    for rcv_inbox in rcv_inboxes:
        if rcv_inbox.startswith(hostname):
            continue

        async def do(rcv_inbox):
            sign("post", rcv_inbox, headers, json.dumps(data), user)

            async with HttpClient().post(rcv_inbox, data=json.dumps(data), headers = headers) as resp:
                if resp.status != 202:
                    print ("Article has not been accepted by target system",rcv_inbox, resp.status)
                return
        tasks.append(do(rcv_inbox))
    await asyncio.gather(*tasks)


async def post_item_to_remote(item: ItemSchema, user: UserSchema):
    item = await item_to_activity(item, user)
    hostname = cfg["General"]["ExternalURL"]
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            {
                "ostatus": "http://ostatus.org#",
                "atomUri": "ostatus:atomUri",
                "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
                "conversation": "ostatus:conversation",
                "sensitive": "as:sensitive",
                "toot": "http://joinmastodon.org/ns#",
                "votersCount": "toot:votersCount",
                "blurhash": "toot:blurhash",
                "focalPoint": {
                    "@container": "@list",
                    "@id": "toot:focalPoint"
                },
                "Hashtag": "as:Hashtag"
            }
        ],
    }
    data.update(item)

    headers = {
        "Content-Type":"application/json"
    }

    rcv_inboxes = await get_inbox_list_from_activity(data)

    tasks = []
    for rcv_inbox in rcv_inboxes:
        if rcv_inbox.startswith(hostname):
            continue

        async def do(rcv_inbox):
            sign("post", rcv_inbox, headers, json.dumps(data), user)

            async with HttpClient().post(rcv_inbox, data=json.dumps(data), headers = headers) as resp:
                if resp.status != 202:
                    print ("Article has not been accepted by target system",rcv_inbox, resp.status)
                return
        tasks.append(do(rcv_inbox))
    await asyncio.gather(*tasks)



async def item_to_note(item: ItemSchema, user: UserSchema):
    hostname = cfg["General"]["ExternalURL"]

    attachments = []
    for image in item["images"]:
        attachments.append({
            "type":"Document",
            "mediaType":"image/jpeg",
            "url": f"{hostname}/api/v1/image/{image}",
            "name": None,
            "width":600,
            "height":400
        })
    return  {
        "id": f"{hostname}/users/{user['name']}/items/{item['id']}",
        "type": "Note",
        "summary": None,
        "inReplyTo": None,
        "published": item["creation_date"].split(".")[0]+"Z",
        "url": f"{hostname}/~{user['name']}/{item['id']}",
        "attributedTo": f"{hostname}/users/{user['name']}",
        "to": [
            "https://www.w3.org/ns/activitystreams#Public"
        ],
        "cc": [
            f"{hostname}/users/{user['name']}/followers"
        ],
        "sensitive": False,
        "content": item["name"] + " <br> " + item["description"],
        "contentMap": {
            "en":item["name"] + " <br> " + item["description"],
        },
        "attachment": attachments,
        "tag": [],
        "replies": {
            "id": f"{hostname}/users/{user['id']}/items/{item['id']}/replies",
            "type": "Collection",
            "first": {
                "type":"CollectionPage",
                "next": f"{hostname}/users/{user['id']}/items/{item['id']}/replies/never",
                "partOf":f"{hostname}/users/{user['id']}/items/{item['id']}/replies",
                "items": []
            }
        }
    }

async def item_to_delete_activity(item: ItemSchema, user: UserSchema):
    hostname = cfg["General"]["ExternalUrl"]

    return {
        "id": f"{hostname}/users/{user['name']}/items/{item['id']}/delete",
        "type": "Delete",
        "actor": f"{hostname}/users/{user['name']}",
        "to": [
            "https://www.w3.org/ns/activitystreams#Public"
        ],
        "object": {
            "id": f"{hostname}/users/{user['name']}/items/{item['id']}",
            "type": "Tombstone",
            "atomUri": f"{hostname}/users/{user['name']}/items/{item['id']}",
        }
    }

async def item_to_activity(item: ItemSchema, user: UserSchema):
    """
    Render an item into its corresponding Create-activity
    """
    hostname = cfg["General"]["ExternalURL"]


    attachments = []
    for image in item["images"]:
        attachments.append({
            "type":"Document",
            "mediaType":"image/jpeg",
            "url": f"{hostname}/api/v1/image/{image}",
            "name": None,
            "width":600,
            "height":400
        })
    return {
        "id": f"{hostname}/users/{user['name']}/items/{item['id']}/activity",
        "type": "Create",
        "actor": f"{hostname}/users/{user['name']}",
        "published": item["creation_date"],
        "to": [
            "https://www.w3.org/ns/activitystreams#Public"
        ],
        "cc": [
            f"{hostname}/users/{user['name']}/followers"
        ],
        "object": {
            "id": f"{hostname}/users/{user['name']}/items/{item['id']}",
            "type": "Note",
            "flohmarkt:data": {
                "price": item["price"],
                "name": item["name"],
                "description": item["description"],
                "original_id": item["id"],
            },
            "summary": None,
            "inReplyTo": None,
            "published": item["creation_date"],
            "url": f"{hostname}/~{user['name']}/{item['id']}",
            "attributedTo": f"{hostname}/users/{user['name']}",
            "to": [
                "https://www.w3.org/ns/activitystreams#Public"
            ],
            "cc": [
                f"{hostname}/users/{user['name']}/followers"
            ],
            "sensitive": False,
            "content": item["name"] + " <br> " + item["description"],
            "contentMap": {
                "en":item["name"] + " <br> " + item["description"],
            },
            "attachment": attachments,
            "tag": [],
            "replies": {
                "id": f"{hostname}/users/{user['id']}/items/{item['id']}/replies",
                "type": "Collection",
                "first": {
                    "type":"CollectionPage",
                    "next": f"{hostname}/users/{user['id']}/items/{item['id']}/replies/never",
                    "partOf":f"{hostname}/users/{user['id']}/items/{item['id']}/replies",
                    "items": []
                }
            }
        }
    }

async def get_item_activity(item: str, user: str):
    item = await ItemSchema.retrieve_single_id(item)
    if item is None:
        raise HTTPException(status_code=404, detail = "Item not found")
    user = await UserSchema.retrieve_single_name(user)
    if user is None:
        raise HTTPException(status_code=404, detail = "User not found")
    item = await item_to_note(item, user)
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            {
                "ostatus": "http://ostatus.org#",
                "conversation": "ostatus:conversation",
                "sensitive": "as:sensitive",
                "toot": "http://joinmastodon.org/ns#",
                "votersCount": "toot:votersCount",
            }
        ],
    }
    data.update(item)
    return data

async def message_to_activity(message: dict):
    """
    Render an item into its corresponding Create-activity
    """
    ret = []
    hostname = cfg["General"]["ExternalURL"]

    return {
        "id": message["id"]+"/activity",
        "type": "Create",
        "actor": message['attributedTo'],
        "published": message["published"],
        "to": message["to"],
        "cc": message["cc"],
        "object": message
    }

async def post_message_remote(message: dict, user: UserSchema):
    message = await message_to_activity(message)
    hostname = cfg["General"]["ExternalURL"]
    data = {
        "@context": [
            "https://www.w3.org/ns/activitystreams",
            {
                "ostatus": "http://ostatus.org#",
                "atomUri": "ostatus:atomUri",
                "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
                "conversation": "ostatus:conversation",
                "sensitive": "as:sensitive",
                "toot": "http://joinmastodon.org/ns#",
                "votersCount": "toot:votersCount",
                "blurhash": "toot:blurhash",
                "focalPoint": {
                    "@container": "@list",
                    "@id": "toot:focalPoint"
                },
                "Hashtag": "as:Hashtag"
            }
        ],
    }
    data.update(message)

    headers = {
        "Content-Type":"application/json"
    }

    for rcv_inbox in await get_inbox_list_from_activity(data):
        if rcv_inbox.startswith(hostname):
            continue
        sign("post", rcv_inbox, headers, json.dumps(data), user)

        async with HttpClient().post(rcv_inbox, data=json.dumps(data), headers = headers) as resp:
            if resp.status != 202:
                print ("Article has not been accepted by target system",rcv_inbox, resp.status)
            return


@router.get("/users/{name}/outbox")
async def user_outbox(name: str, page : bool = False, min_id : str = ""):
    hostname = cfg["General"]["ExternalURL"]
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")
    if page:
        items = await ItemSchema.retrieve_by_user(user['id'])

        activities = [await item_to_activity(x) for x in items]

        return {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                {
                    "ostatus": "http://ostatus.org#",
                    "atomUri": "ostatus:atomUri",
                    "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
                    "conversation": "ostatus:conversation",
                    "sensitive": "as:sensitive",
                    "toot": "http://joinmastodon.org/ns#",
                    "votersCount": "toot:votersCount",
                    "blurhash": "toot:blurhash",
                    "focalPoint": {
                        "@container": "@list",
                        "@id": "toot:focalPoint"
                    },
                    "Hashtag": "as:Hashtag"
                }
            ],
            "id": f"{hostname}/users/{user['name']}/outbox?page=true",
            "type": "OrderedCollectionPage",
            "prev": f"{hostname}/users/{user['name']}/outbox?min_id=110040056389441342&page=true", #TODO fill
            "partOf": f"{hostname}/users/{user['name']}/outbox",
            "orderedItems": activities
            
        }
    else:
        return {
            "@context":"https://www.w3.org/ns/activitystreams",
            "id":f"{hostname}/users/{user['name']}/outbox",
            "type":"OrderedCollection",
            "totalItems":1, # TODO fill
            "first":f"{hostname}/users/{user['name']}/outbox?page=true"
        }

@router.get("/users/{name}", response_description="User Activitypub document")
async def user(name: str):
    user = await UserSchema.retrieve_single_name(name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found :(")
    username = user["name"]
    public_key = user.get("public_key", "")
    hostname = cfg["General"]["ExternalURL"]
    ret = {
      "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {
          "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
          "toot": "http://joinmastodon.org/ns#",
          "featured": {
            "@id": "toot:featured",
            "@type": "@id"
          },
          "featuredTags": {
            "@id": "toot:featuredTags",
            "@type": "@id"
          },
          "alsoKnownAs": {
            "@id": "as:alsoKnownAs",
            "@type": "@id"
          },
          "movedTo": {
            "@id": "as:movedTo",
            "@type": "@id"
          },
          "schema": "http://schema.org#",
          "PropertyValue": "schema:PropertyValue",
          "value": "schema:value",
          "discoverable": "toot:discoverable",
          "Device": "toot:Device",
          "Ed25519Signature": "toot:Ed25519Signature",
          "Ed25519Key": "toot:Ed25519Key",
          "Curve25519Key": "toot:Curve25519Key",
          "EncryptedMessage": "toot:EncryptedMessage",
          "publicKeyBase64": "toot:publicKeyBase64",
          "deviceId": "toot:deviceId",
          "claim": {
            "@type": "@id",
            "@id": "toot:claim"
          },
          "fingerprintKey": {
            "@type": "@id",
            "@id": "toot:fingerprintKey"
          },
          "identityKey": {
            "@type": "@id",
            "@id": "toot:identityKey"
          },
          "devices": {
            "@type": "@id",
            "@id": "toot:devices"
          },
          "messageFranking": "toot:messageFranking",
          "messageType": "toot:messageType",
          "cipherText": "toot:cipherText",
          "suspended": "toot:suspended"
        }
      ],
      "id": f"{hostname}/users/{username}",
      "type": "Person",
      "following": f"{hostname}/users/{username}/following",
      "followers": f"{hostname}/users/{username}/followers",
      "inbox": f"{hostname}/users/{username}/inbox",
      "outbox": f"{hostname}/users/{username}/outbox",
      "featured": f"{hostname}/users/{username}/collections/featured",
      "featuredTags": f"{hostname}/users/{username}/collections/tags",
      "preferredUsername": f"{username}",
      "name": f"{username}",
      "summary": "",
      "url": f"{hostname}/~{username}",
      "manuallyApprovesFollowers": False,
      "discoverable": False,
      "published": "2023-03-07T00:00:00Z",
      "devices": f"{hostname}/users/{username}/collections/devices",
      "publicKey": {
        "id": f"{hostname}/users/{username}#main-key",
        "owner": f"{hostname}/users/{username}",
        "publicKeyPem": public_key
      },
      "tag": [],
      "attachment": [],
      "endpoints": {
        "sharedInbox": f"{hostname}/inbox"
      }
    }
    if user["avatar"] is not None:
      ret["icon"] = {
        "type":"Image",
        "mediaType": "image/jpeg",
        "url": f"{hostname}/api/v1/image/{user['avatar']}"
      }

    return ret

