from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema
from flohmarkt.routes.activitypub import replicate_user

router = APIRouter()

@router.get("/by_remote", response_description="The url of a user avatar")
async def get_avatar(url:str):
    user = await UserSchema.retrieve_single_remote_url(url)
    if user is None:
        try:
            # TODO: replace with eventual consistency
            #       implement a background service that 
            #       fetches and checks users against local data
            user = await replicate_user(url)
        except Exception as e:
            raise HTTPException(status_code=404, detail="User is not beer :(")
    await UserSchema.filter(user)
    return user
