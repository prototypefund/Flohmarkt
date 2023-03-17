from fastapi import APIRouter, Body, HTTPException

from flohmarkt.models.user import UserSchema, UpdateUserModel

router = APIRouter()

@router.get("/.well-known/webfinger", response_description="Check for user")
async def add_item(resource: str):
    return {
            "subject" : "acct:grindolite@testcontainer.lan",
            "aliases": [
                "https://testcontainer.lan/~grindolite",
                "https://testcontainer.lan/users/grindolite",
            ],
            "links": [
                {
                    "rel": "http://webfinger.net/rel/profile-page",
                    "type": "text/html",
                    "href": "https://testcontainer.lan/~grindolite"
                },
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": "https://testcontainer.lan/users/grindolite"
                },
                {
                    "rel": "http://ostatus.org/schema/1.0/subscribe",
                    "template" : "https://testcontainer.lan/authorize_interaction?uri={ uri }"
                }
            ]
    }

