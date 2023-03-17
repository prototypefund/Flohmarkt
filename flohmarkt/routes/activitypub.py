from fastapi import APIRouter, HTTPException, Body

from flohmarkt.models.user import UserSchema, UpdateUserModel

router = APIRouter()

@router.post("/inbox")
async def inbox(name: str, msg : dict = Body(...) ):
    print(msg)
    return {}

@router.get("/users/{name}/followers")
async def followers():
    return {}

@router.get("/users/{name}/following")
async def following():
    return {}

@router.post("/users/{name}/inbox")
async def user_inbox(name: str, msg : dict = Body(...) ):
    print(msg)
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
    hostname = "testcontainer.lan"
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
      "id": f"https://{hostname}/users/{username}",
      "type": "Person",
      "following": f"https://{hostname}/users/{username}/following",
      "followers": f"https://{hostname}/users/{username}/followers",
      "inbox": f"https://{hostname}/users/{username}/inbox",
      "outbox": f"https://{hostname}/users/{username}/outbox",
      "featured": f"https://{hostname}/users/{username}/collections/featured",
      "featuredTags": f"https://{hostname}/users/{username}/collections/tags",
      "preferredUsername": f"{username}",
      "name": f"{username}",
      "summary": "",
      "url": f"https://{hostname}/~{username}",
      "manuallyApprovesFollowers": False,
      "discoverable": False,
      "published": "2023-03-07T00:00:00Z",
      "devices": f"https://{hostname}/users/{username}/collections/devices",
      "publicKey": {
        "id": f"https://{hostname}/users/{username}#main-key",
        "owner": f"https://{hostname}/users/{username}",
        "publicKeyPem": "-----BEGIN PUBLIC KEY-----\\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyM35mRSQj9O2hUaaTREO\\nL4qTgNx3MsvvM8MADHbYm2EgDKB+4O/hb7CKO9j7QUvS75xDpSx4PeoQuQz9nXC4\\nXeG4d+a4xZ6rPJ/mcrV4G99BTlfJwRigHa4Giavz4YyInRvambkf2qS4T2HGG2GN\\n8Wj4FFw0QLxUodfaEIfJCiZa+0e9Dpt2AaQv8WXcgQ0FFEuhq1ktXJmUjv+H0rUL\\nh2lp4JcPptmo97Lv50QfDSTFPkfPJ69QwMHXixuPpxRfk7NZlyl65Z+uZ5ZcuA01\\nGCDG2KDk0QXZKXIjpELuSwo3Vyp/mdYhcMCg6A24DD+VAMuIkW5GFpXTJJLTcUmy\\nDQIDAQAB\\n-----END PUBLIC KEY-----\\n"
      },
      "tag": [],
      "attachment": [],
      "endpoints": {
        "sharedInbox": f"https://{hostname}/inbox"
      }
    }

