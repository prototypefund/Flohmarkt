import json
import asyncio
import aiohttp

from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import JSONResponse, Response
from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.signatures import verify, sign
from flohmarkt.http import HttpClient
from flohmarkt.models.user import UserSchema
from flohmarkt.models.follow import AcceptSchema

router = APIRouter()

"""
{
  "@context":"https://www.w3.org/ns/activitystreams",
  "id":"https://mastodont.lan/users/grindhold#accepts/follows/42",
  "type":"Accept",
  "actor":"https://mastodont.lan/users/grindhold",
  "object":{"id":"https://mastodo.lan/fe65ad92-500f-4333-bc9a-945e4559497f","type":"Follow","actor":"https://mastodo.lan/users/grindhold","object":"https://mastodont.lan/users/grindhold"}}
"""


def get_actor_name(user):
    return 

async def get_userinfo(actor : str) -> dict:
    async with HttpClient().get(actor, headers = {
            "Accept":"application/json"
        }) as resp:
        return await resp.json()

async def accept(rcv_inbox, follow, user):
    accept = AcceptSchema(
        object=follow,
        id = cfg["General"]["ExternalURL"]+f"/users/{user['name']}#accepts/follows/42",
        type = "Accept",
        actor = user['id'],
        context = "https://www.w3.org/ns/activitystreams"
    )
    #TODO determine numbers
    accept = jsonable_encoder(accept)
    headers = {
        "Content-Type":"application/json"
    }
    sign("post", rcv_inbox, headers, json.dumps(accept), user)
    print(headers)
    async with HttpClient().post(rcv_inbox, data=json.dumps(accept), headers = headers) as resp:
        print (resp.status)
        #print (resp)
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
async def followers():
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")
    return user.followers

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

@router.post("/users/{name}/outbox")
async def user_outbox():
    return {}

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

