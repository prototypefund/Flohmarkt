from fastapi import APIRouter, Body, Depends, Request
from fastapi.encoders import jsonable_encoder

@router.post("/", response_description="Added")
async def add_item(request: Request, item: ItemSchema = Body(...), 
                   current_user: UserSchema = Depends(get_current_user)):
    item = jsonable_encoder(item)
    item["user"] = current_user["id"]
    new_item = await ItemSchema.add(item)
    await post_to_remote(new_item, current_user)
    return new_item
