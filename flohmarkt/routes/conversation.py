from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.item import ItemSchema
from flohmarkt.models.conversation import ConversationSchema
from flohmarkt.auth import oauth2, get_current_user

router = APIRouter()


@router.get("/by_item/{item_id}", response_description="A single user if any")
async def _(item_id:str, current_user: UserSchema = Depends(get_current_user)):
    item = await ItemSchema.retrieve_single_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, details="User is not here :(")

    if item["user"] != current_user["id"]:
        raise HTTPException(status_code=403, details="Only the owner of the thing may do this :(")

    conversations = await ConversationSchema.retrieve_for_item(item['id'])
    return conversations

@router.post("/{ident}", response_description="Update stuff")
async def update_user(ident: str, req: MessageSchema = Body(...), current_user: UserSchema = Depends(get_current_user)):
    print(msg)

@router.delete("/{ident}", response_description="deleted")
async def delete_user(ident: str):
    await UserSchema.delete(ident)
    return "SUS"
