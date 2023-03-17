from fastapi import APIRouter, HTTPException, Body

from flohmarkt.config import cfg
from flohmarkt.models.user import UserSchema, UpdateUserModel

router = APIRouter()

async def follow(obj):
    name = obj['object'].replace(cfg["General"]["ExternalURL"]+"/users/","",1)
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")
    if "followers" not in user:
        user["followers"] = {}
    user["followers"][obj['id']] = obj
    await user.update(user['id'], user)
    return {}

async def unfollow(obj):
    name = obj['object']['object'].replace(cfg["General"]["ExternalURL"]+"/users/","",1)
    user = await UserSchema.retrieve_single_name(name)
    if user is None:
        raise HTTPException(status_code=404, detail="No such user :(")
    if "followers" in user:
        del(user["followers"][obj['object']['id']])
    await user.update(user['id'], user)
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
async def user_inbox(name: str, msg : dict = Body(...) ):
    print(msg)
    if msg['type'] == "Follow":
        return await follow(msg)
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
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found :(")
    username = user["name"]
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
        "publicKeyPem": "-----BEGIN PUBLIC KEY-----\\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyM35mRSQj9O2hUaaTREO\\nL4qTgNx3MsvvM8MADHbYm2EgDKB+4O/hb7CKO9j7QUvS75xDpSx4PeoQuQz9nXC4\\nXeG4d+a4xZ6rPJ/mcrV4G99BTlfJwRigHa4Giavz4YyInRvambkf2qS4T2HGG2GN\\n8Wj4FFw0QLxUodfaEIfJCiZa+0e9Dpt2AaQv8WXcgQ0FFEuhq1ktXJmUjv+H0rUL\\nh2lp4JcPptmo97Lv50QfDSTFPkfPJ69QwMHXixuPpxRfk7NZlyl65Z+uZ5ZcuA01\\nGCDG2KDk0QXZKXIjpELuSwo3Vyp/mdYhcMCg6A24DD+VAMuIkW5GFpXTJJLTcUmy\\nDQIDAQAB\\n-----END PUBLIC KEY-----\\n"
      },
      "tag": [],
      "attachment": [],
      "endpoints": {
        "sharedInbox": f"{hostname}/inbox"
      }
    }

