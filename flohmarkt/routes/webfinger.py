from fastapi import APIRouter, Body, HTTPException, Response

from flohmarkt.config import cfg
from flohmarkt.models.user import UserSchema, UpdateUserModel

router = APIRouter()

@router.get("/.well-known/host-meta", response_description="host meta info xml")
async def hostmeta():
    url = cfg["General"]["ExternalURL"]
    content = f"""<?xml version="1.0" encoding="UTF-8"?>
<XRD xmlns="http://docs.oasis-open.org/ns/xri/xrd-1.0">
    <Link rel="lrdd" template="{url}/.well-known/webfinger?resource={{uri}}"/>
</XRD>"""
    return Response(content=content, headers={"Content-type":"text/xml"}, status_code=200)

@router.get("/.well-known/webfinger", response_description="Check for user")
async def webfinger(resource: str):
    username = resource.split("@")[0]
    username = username.replace("acct:","",1)
    user = await UserSchema.retrieve_single_name(username)

    if user:
        url = cfg["General"]["ExternalURL"]
        hostname = url.replace("https://","",1).replace("http://","",1)

        return {
                "subject" : f"acct:{user['name']}@{hostname}",
                "aliases": [
                    f"{url}/~{user['name']}",
                    f"{url}/users/{user['name']}",
                ],
                "links": [
                    {
                        "rel": "http://webfinger.net/rel/profile-page",
                        "type": "text/html",
                        "href": f"{url}/~{user['name']}"
                    },
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": f"{url}/users/{user['name']}"
                    },
                    {
                        "rel": "http://ostatus.org/schema/1.0/subscribe",
                        "template" : f"{url}/authorize_interaction?uri="+"{ uri }"
                    }
                ]
        }
    else:
        raise HTTPException(status_code=404, detail="User not here :(")

