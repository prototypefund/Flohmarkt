from fastapi import APIRouter, Body, HTTPException

from flohmarkt.config import cfg
from flohmarkt.models.user import UserSchema, UpdateUserModel

router = APIRouter()

@router.get("/.well-known/webfinger", response_description="Check for user")
async def add_item(resource: str):
    username = resource.split("@")[0]
    username = username.replace("acct:","",1)
    user = await UserSchema.retrieve_single_name(username)

    if user:
        hostname = cfg["General"]["ExternalURL"]
        hostname = hostname.replace("https://","",1).replace("http://","",1)

        return {
                "subject" : f"acct:{user['name']}@{hostname}",
                "aliases": [
                    f"{hostname}/~{user['name']}",
                    f"{hostname}/users/{user['name']}",
                ],
                "links": [
                    {
                        "rel": "http://webfinger.net/rel/profile-page",
                        "type": "text/html",
                        "href": f"{hostname}/~{user['name']}"
                    },
                    {
                        "rel": "self",
                        "type": "application/activity+json",
                        "href": f"{hostname}/users/{user['name']}"
                    },
                    {
                        "rel": "http://ostatus.org/schema/1.0/subscribe",
                        "template" : f"{hostname}/authorize_interaction?uri="+"{ uri }"
                    }
                ]
        }
    else:
        raise HTTPException(status_code=404, detail="User not here :(")

