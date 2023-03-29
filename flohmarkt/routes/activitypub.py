import json
import asyncio
import aiohttp

from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder
from typing import List

from flohmarkt.config import cfg
from flohmarkt.signatures import verify, sign
from flohmarkt.http import HttpClient
from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema
from flohmarkt.models.follow import AcceptSchema

router = APIRouter()

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
        print (resp.status)
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

@router.post("/inbox")
async def inbox(msg : dict = Body(...) ):
    print(msg)
    return {}

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
            "totalItems":len(user["followers"]),
            "first":f"{hostname}/users/{user['name']}/followers?page=1"
        }
    else:
        if page < 1:
            raise HTTPException(status_code=404, detail="Page not found :(")
        return {
            "@context":"https://www.w3.org/ns/activitystreams",
            "id":f"{hostname}/users/{user['name']}/followers?page=1",
            "type":"OrderedCollectionPage",
            "totalItems":len(user["followers"]),
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

async def items_to_activity(items: List[ItemSchema], user: UserSchema):
    ret = []
    hostname = cfg["General"]["ExternalURL"]

    for item in items:
        attachments = []
        for image in item["images"]:
            attachments.append({
                "type":"Document",
                "mediaType":"image/jpeg",
                "url": f"{hostname}/api/v1/images/{image}",
                "name": None,
                "width":600,
                "height":400
            })
        ret.append({
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
                "replies": None
            }
        })
    return ret

@router.get("/users/{name}/outbox")
async def user_outbox(name: str, page : bool = False, min_id : str = ""):
    hostname = cfg["General"]["ExternalURL"]
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")
    if page:
        items = await ItemSchema.retrieve_by_user(user['id'])

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
            "orderedItems": await items_to_activity(items, user)
            
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
    return {
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

