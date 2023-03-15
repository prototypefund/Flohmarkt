from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.item import ItemSchema, UpdateItemModel
from flohmarkt.auth import oauth2

router = APIRouter()

@router.post("/", response_description="Added")
async def add_item(item: ItemSchema = Body(...)):
    item = jsonable_encoder(item)
    new_item = await ItemSchema.add(item)
    return new_item

@router.get("/", response_description="All items")
async def get_items():
    items = await ItemSchema.retrieve()
    return items

@router.get("/{ident}", response_description="A single item if any")
async def get_item(ident:str):
    print("IN ROUTE", ident)
    item = await ItemSchema.retrieve_single(ident)
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
