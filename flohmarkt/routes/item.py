from fastapi import APIRouter, Body, Depends, Request
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema, UpdateItemModel
from flohmarkt.auth import get_current_user
from flohmarkt.routes.activitypub import post_to_remote

router = APIRouter()

@router.post("/", response_description="Added")
async def add_item(request: Request, item: ItemSchema = Body(...), 
                   current_user: UserSchema = Depends(get_current_user)):
    item = jsonable_encoder(item)
    item["user"] = current_user["id"]
    new_item = await ItemSchema.add(item)
    await post_to_remote(new_item, current_user)
    return new_item

@router.get("/", response_description="All items")
async def get_items():
    items = await ItemSchema.retrieve()
    return items

#TODO: implement
@router.get("/most_contested", response_description="All items")
async def get_items():
    #items = await ItemSchema.retrieve()
    #TODO: implement
    return []

@router.get("/newest", response_description="Newest items")
async def get_items():
    return await ItemSchema.retrieve_newest()

@router.get("/search/{searchterm}", response_description="Search results")
async def get_items(searchterm: str):
    return await ItemSchema.search(searchterm)

@router.get("/oldest", response_description="Oldest items")
async def get_items():
    return await ItemSchema.retrieve_oldest()

@router.get("/by_user/{user_id}", response_description="All items of user")
async def get_items(user_id: str):
    return await ItemSchema.retrieve_by_user(user_id)

@router.get("/{ident}", response_description="A single item if any")
async def get_item(ident:str):
    print("IN ROUTE", ident)
    item = await ItemSchema.retrieve_single_id(ident)
    return item

@router.put("/{ident}", response_description="Update stuff")
async def update_item(ident: str, req: UpdateItemModel = Body(...)):
    req = {k: v for k,v in req.dict().items() if v is not None}
    updated_item = await ItemSchema.update(ident, req)
    if updated_item:
        return "YEEEH"
    return "NOOO"

@router.delete("/{ident}", response_description="deleted")
async def delete_item(ident: str):
    await ItemSchema.delete(ident)
    return "SUS"
