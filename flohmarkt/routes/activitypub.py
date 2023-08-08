import json
import asyncio
import re
import os
import uuid
import datetime
import aiohttp
import hashlib

from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from typing import List

from flohmarkt.geo import is_inside_perimeter
from flohmarkt.config import cfg
from flohmarkt.signatures import verify, sign
from flohmarkt.socketpool import Socketpool
from flohmarkt.http import HttpClient
from flohmarkt.routes.image import assert_imagepath
from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema
from flohmarkt.models.instance_settings import InstanceSettingsSchema
from flohmarkt.models.conversation import ConversationSchema
from flohmarkt.models.follow import AcceptSchema

router = APIRouter()
uuid_regex = re.compile('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)

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

async def get_userinfo(actor : str) -> dict:
    async with HttpClient().get(actor, headers = {
            "Accept":"application/json,application/ld+json,application/activity+json"
        }) as resp:
        return await resp.json()

async def accept(rcv_inbox, follow, user):
    hostname = cfg["General"]["ExternalURL"]
    print(follow) #TODO remove. This is trapcode for a follow issue with a specific system
    if type(follow.get("@context", None)) != str:
        follow["@context"] = "https://www.w3.org/ns/activitystreams"
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

async def replicate_item(item_url : str) -> ItemSchema:
    headers = { "Accept": "application/json,application/ld+json,application/activity+json" }
    try:
        async with HttpClient().get(item_url, headers=headers) as resp:
            res = await resp.json()
            if res["type"] == "Note":
                user = await replicate_user(res["attributedTo"])
                item = await wrap_note_in_activity(res, user)
                item = await append_context(item)
                return await create_new_item(item)
    except asyncio.exceptions.TimeoutError:
        raise Exception(f"Timed out replicating : {item_url}")
    except Exception as e:
        raise (e) 

async def replicate_image(image_url : str) -> str:
    ident = image_url.split("/")[-1]
    if not uuid_regex.match (ident):
        ident = str(uuid.uuid4())

    await assert_imagepath()
    imagepath = os.path.join(cfg["General"]["DataPath"], "images", ident)

    async with HttpClient().get(image_url) as resp:
        imagefile = open(imagepath, "wb")
        imagefile.write(await resp.read())
        imagefile.close()
        return (image_url, ident)

async def replicate_user(user_url: str) -> str:
    ident = user_url.split("/")[-1]

    if not uuid_regex.match (ident):
        m = hashlib.md5()
        m.update(user_url.encode('utf-8'))
        ident = str(uuid.UUID(m.hexdigest()))

    async with HttpClient().get(user_url, headers = {
            "Accept":"application/json,application/ld+json,application/activity+json"
        }) as resp:
        userinfo = await resp.json()
        parsed = urlparse(user_url)

        provided_name = userinfo["preferredUsername"].split("@")[0]
        
        username = provided_name+"@"+parsed.netloc

        user = await UserSchema.retrieve_single_name(username)
        if user is not None:
            return user

        avatar = None
        if "icon" in userinfo:
            async with HttpClient().get(userinfo["icon"]["url"]) as resp:
                await assert_imagepath()
                image = await resp.read()

                avatar = str(uuid.uuid4())

                imagefile = open(os.path.join(cfg["General"]["DataPath"],"images", avatar), "wb")
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
            "public_key": userinfo["publicKey"]["publicKeyPem"],
        }
        await UserSchema.replicate(new_user)
        return new_user

async def create_new_item(msg: dict):
    hostname = cfg["General"]["ExternalURL"]

    if not "flohmarkt:data" in msg["object"]:
        raise HTTPException(status_code=422, detail="Does not seem to be a flohmarkt item")

    tasks = []
    for attachment in msg["object"].get("attachment",[]):
        tasks.append(replicate_image(attachment["url"]))
    url_id_map = await asyncio.gather(*tasks)
    url_id_dict = {k: v for k,v in url_id_map}
    images = [
        {
            "image_id": url_id_dict[a["url"]],
            "description": a["name"]
        } for a in msg["object"]["attachment"]
    ]

    user = await UserSchema.retrieve_single_remote_url(msg["object"]["attributedTo"])
    if user is None:
        user = await replicate_user(msg["object"]["attributedTo"])

    if not (await is_inside_perimeter(msg["object"]["flohmarkt:data"]["coordinates"])):
        raise HTTPException(status_code=403, detail="Cannot accept item beyond perimeter")

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
        "user": user["id"],
        "url": msg["object"]["url"],
        "images": images
    }
    item = await ItemSchema.add(item, user)
    return item

async def send_blocked_user_message(msg):
    hostname = cfg["General"]["ExternalURL"]
    item_id = msg["object"]["inReplyTo"].split("/")[-1]
    item = await ItemSchema.retrieve_single_id(item_id)
    user = await UserSchema.retrieve_single_id(item["user"])
    
    msg["text"] = f"Sorry, you are blocked on {hostname}"
 
    message = await convert_to_activitypub_message(msg, user, parent=msg["object"], item=item)
    await post_message_remote(message, user)

async def send_blocked_instance_message(msg):
    hostname = cfg["General"]["ExternalURL"]
    item_id = msg["object"]["inReplyTo"].split("/")[-1]
    item = await ItemSchema.retrieve_single_id(item_id)
    user = await UserSchema.retrieve_single_id(item["user"])
    
    msg["text"] = f"Sorry, your instance is blocked on {hostname}"
 
    message = await convert_to_activitypub_message(msg, user, parent=msg["object"], item=item)
    await post_message_remote(message, user)


async def send_noreply_message(msg):
    item_id = msg["object"]["inReplyTo"].split("/")[-1]
    item = await ItemSchema.retrieve_single_id(item_id)
    user = await UserSchema.retrieve_single_id(item["user"])
    
    msg["text"] = """You've made a public post to a item on flohmarkt.
 <b>This post is going to be ignored by the system.</b>
 Please use private posting e.g. 'Only mentioned' in mastodon.
 (This is a system-generated message)"""
 
    message = await convert_to_activitypub_message(msg, user, parent=msg["object"], item=item)
    await post_message_remote(message, user)

async def inbox_process_create(req: Request, msg: dict):
    hostname = cfg["General"]["ExternalURL"]
    if msg["id"].startswith(hostname):
        raise HTTPException(status_code=302, detail="Already exists")

    if "https://www.w3.org/ns/activitystreams#Public" in msg["to"]:
        if "object" in msg and "inReplyTo" in msg["object"] and msg["object"]["inReplyTo"] is not None:
            await send_noreply_message(msg)
            return Response(content="0", status_code=202)
        else:
            await create_new_item(msg)
            return Response(content="0", status_code=202)

    if len(msg["to"]) != 1:
        raise HTTPException(status_code=400, detail="Can only accept private messages to 1 user")

    username = msg["to"][0].replace(f"{hostname}/users/","")
    user = await UserSchema.retrieve_single_name(username)

    if user is None:
        raise HTTPException(status_code=404, detail="Targeted user not found")

    item = None
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


    is_new_conversation = False
    if conversation is None:
        if item is None:
            raise HTTPException(status_code=404, detail="Targeted item not found")
        is_new_conversation = True
        conversation = {
            "user_id" : user['id'],
            "remote_user" : msg["actor"],
            "item_id" : item['id'],
            "messages" : []
        }
        conversation = await ConversationSchema.add(conversation)

    conversation["messages"].append(msg["object"])

    if msg["actor"] == conversation["remote_user"]:
        receiver = await UserSchema.retrieve_single_id(conversation["user_id"])
    else:
        receiver = await UserSchema.retrieve_single_remote_url(conversation["remote_user"])
    if receiver is not None:
        receiver["has_unread"] = True
        await UserSchema.update(receiver["id"], receiver)

    await ConversationSchema.update(conversation['id'], conversation)
    if is_new_conversation:
        await Socketpool.send_conversation(jsonable_encoder(conversation))
    else:
        await Socketpool.send_message(msg["object"])

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

    if msg["actor"] == conversation["remote_user"]:
        receiver = await UserSchema.retrieve_single_id(conversation["user_id"])
    else:
        receiver = await UserSchema.retrieve_single_remote_url(conversation["remote_user"])
    if receiver is not None:
        receiver["has_unread"] = True
        await UserSchema.update(receiver["id"], receiver)

    await ConversationSchema.update(conversation['id'], conversation)
    await Socketpool.send_message(msg["object"])

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
        print("trying to delete msg: "+msg["object"]["id"])
        conv = await ConversationSchema.retrieve_for_message_id(msg["object"]["id"])
        if conv is None:
            return
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

    print(json.dumps(msg))
    user = await UserSchema.retrieve_single_remote_url(msg["actor"])
    if not await verify(req, user):
        if msg["actor"] == msg["object"] and msg["type"] == "Delete":
            return Response(status_code=410)
        raise HTTPException(status_code=401, detail="request signature could not be validated")

    if msg["actor"] == msg["object"] and msg["type"] == "Delete":
        await UserSchema.delete(user["id"])
        return Response(status_code=410)

    instance_settings = await InstanceSettingsSchema.retrieve()
    blocked_users = instance_settings.get("blocked_users",[])
    if msg["actor"]  in blocked_users:
        await send_blocked_user_message(msg)
        raise HTTPException(status_code=403, detail="User is blocked")
        
    blocked_instances = instance_settings.get("blocked_instances",[])
    parsed = urlparse(msg["actor"])
    instance_url = parsed.scheme+"://"+parsed.netloc
    if instance_url in blocked_instances:
        await send_blocked_instance_message(msg)
        raise HTTPException(status_code=403, detail="Instance is blocked")

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
    print(msg)

    if not await verify(req):
        raise HTTPException(status_code=401, detail="request signature could not be validated")
    if msg['type'] == "Follow":
        result = await follow(msg)
        return Response(content="0", status_code=202)
    if msg['type'] == "Create":
        return await inbox_process_create(req, msg)
    if msg['type'] == "Update":
        return await inbox_process_update(req, msg)
    if msg['type'] == "Delete":
        return await inbox_process_delete(req, msg)
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
        "Content-Type":"application/ld+json"
    }

    rcv_inboxes = await get_inbox_list_from_activity(data)

    tasks = []
    for rcv_inbox in rcv_inboxes:
        if rcv_inbox.startswith(hostname):
            continue

        async def do(rcv_inbox):
            sign("post", rcv_inbox, headers, json.dumps(data), user)

            try:
                async with HttpClient().post(rcv_inbox, data=json.dumps(data), headers = headers) as resp:
                    if resp.status != 202:
                        print ("Article has not been accepted by target system",rcv_inbox, resp.status)
                    return
            except aiohttp.client_exceptions.ClientConnectorError:
                print(f"Could not deliver itemdelete to {rcv_inbox}: Unable to connect")
            except aiohttp.client_exceptions.ServerTimeoutError:
                print(f"Could not deliver itemdelete to {rcv_inbox}: Server timeout")
        tasks.append(do(rcv_inbox))
    await asyncio.gather(*tasks)


async def post_item_to_remote(item: ItemSchema, user: UserSchema):
    item = await item_to_activity(item, user)
    hostname = cfg["General"]["ExternalURL"]
    item = await append_context(item)
    headers = {
        "Content-Type":"application/ld+json"
    }

    rcv_inboxes = await get_inbox_list_from_activity(item)

    tasks = []
    for rcv_inbox in rcv_inboxes:
        if rcv_inbox.startswith(hostname):
            continue

        async def do(rcv_inbox):
            sign("post", rcv_inbox, headers, json.dumps(item), user)

            try:
                async with HttpClient().post(rcv_inbox, data=json.dumps(item), headers = headers) as resp:
                    if not resp.status in (200, 202):
                        print ("Article has not been accepted by target system",rcv_inbox, resp.status)
                    return
            except aiohttp.client_exceptions.ClientConnectorError:
                print(f"Could not deliver item to {rcv_inbox}: Unable to connect")
            except aiohttp.client_exceptions.ServerTimeoutError:
                print(f"Could not deliver item to {rcv_inbox}: Server timeout")
        tasks.append(do(rcv_inbox))
    await asyncio.gather(*tasks)



async def item_to_note(item: ItemSchema, user: UserSchema):
    hostname = cfg["General"]["ExternalURL"]

    attachments = []
    for image in item["images"]:
        ident = image["image_id"]
        attachments.append({
            "type":"Document",
            "mediaType":"image/jpeg",
            "url": f"{hostname}/api/v1/image/{ident}",
            "name": image["description"],
            "width":600,
            "height":400
        })

    settings = await InstanceSettingsSchema.retrieve()

    utcdate = datetime.datetime.utcfromtimestamp(
        datetime.datetime.fromisoformat(item["creation_date"]).timestamp()
    ).isoformat().split(".")[0]+"Z"

    return  {
        "id": f"{hostname}/users/{user['name']}/items/{item['id']}",
        "type": "Note",
        "flohmarkt:data": {
            "price": item["price"],
            "name": item["name"],
            "description": item["description"],
            "original_id": item["id"],
            "coordinates": settings["coordinates"],
        },
        "summary": None,
        "inReplyTo": None,
        "published": utcdate,
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

    note = await item_to_note(item, user)

    utcdate = datetime.datetime.utcfromtimestamp(
        datetime.datetime.fromisoformat(item["creation_date"]).timestamp()
    ).isoformat().split(".")[0]+"Z"

    return {
        "id": f"{hostname}/users/{user['name']}/items/{item['id']}/activity",
        "type": "Create",
        "actor": f"{hostname}/users/{user['name']}",
        "published": utcdate,
        "to": [
            "https://www.w3.org/ns/activitystreams#Public"
        ],
        "cc": [
            f"{hostname}/users/{user['name']}/followers"
        ],
        "object": note
    }

async def wrap_note_in_activity(item: dict, user: UserSchema):
    """
    Render an item into its corresponding Create-activity
    """
    hostname = cfg["General"]["ExternalURL"]

    return {
        "id": f"{hostname}/users/{user['name']}/items/{item['id']}/activity",
        "type": "Create",
        "actor": f"{hostname}/users/{user['name']}",
        "published": item["published"],
        "to": [
            "https://www.w3.org/ns/activitystreams#Public"
        ],
        "cc": [
            f"{hostname}/users/{user['name']}/followers"
        ],
        "object": item
    }

async def append_context(message: dict):
    """
    Place @context at the outermost level. remove inner @contexts if present.
    """
    def remove_inner_context(m: dict):
        if "@context" in m:
            del(m["@context"])
        for _, v in m.items():
            if type(v) == dict:
                remove_inner_context(v)

    remove_inner_context(message)
    message["@context"] = [
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
    ]
    return message
            


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

    message = await append_context(message)

    headers = {
        "Content-Type":"application/json"
    }

    for rcv_inbox in await get_inbox_list_from_activity(message):
        if rcv_inbox.startswith(hostname):
            continue
        sign("post", rcv_inbox, headers, json.dumps(message), user)

        async with HttpClient().post(rcv_inbox, data=json.dumps(message), headers = headers) as resp:
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

@router.get("/remote-interact", response_description="User Activitypub document")
async def user_route(req : Request, acc: str):
    if not "@" in acc:
        raise HTTPException(status_code=400, detail="fediverse account must contain @")


    acc = acc.lstrip("@") # for mastodon
    name, host = acc.split("@")
    webfinger_url = "https://"+host+"/.well-known/webfinger?resource=acct:"+acc
    async with HttpClient().get(webfinger_url) as r:
        json = await r.json()
        print("remote-interact", json)
        if not "links" in json:
            raise HTTPException(status_code=403, detail="Remote instance does not support interaction")
        for link in json['links']:
            if link["rel"] == "http://ostatus.org/schema/1.0/subscribe":
                return {"url":link["template"]}

        raise HTTPException(status_code=403, detail="Remote instance doesn't support interaction")
    

@router.get("/users/{name}", response_description="User Activitypub document")
async def user_route(name: str):
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
        "mediaType": "image/*",
        "url": f"{hostname}/api/v1/image/{user['avatar']}"
      }

    return ret

