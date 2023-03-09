from typing import Optional
from pydantic import BaseModel, Field
from bson.objectid import ObjectId

from flohmarkt.db import db, rename_id

item_collection = db.get_collection("items")

class ModeEnum:
    SELL = 0
    GIVEAWAY = 1

class ItemSchema(BaseModel):
    name : str = Field(...)
    
    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
        }
    @staticmethod
    async def retrieve():
        items = []
        async for item in item_collection.find():
            items.append(rename_id(item))
        return items

    @staticmethod
    async def add(data: dict)->dict:
        ins = await item_collection.insert_one(data)
        new = await item_collection.find_one({"_id":ins.inserted_id})
        return rename_id(new)

    @staticmethod
    async def retrieve_single(ident: str)->dict:
        print(ident)
        item = await item_collection.find_one({"_id":ObjectId(ident)})
        if item is not None:
            return rename_id(item)

    @staticmethod
    async def update(ident: str, data: dict):
        if len(data) < 1:
            return False
        item = await item_collection.find_one({"_id":ObjectId(ident)})
        if item is not None:
            updated = await item_collection.update_one(
                    {"_id":ObjectId(ident)}, {"$set": data}
            )
            if updated is not None:
                return True
            return False

    @staticmethod
    async def delete(ident : str):
        item = await item_collection.find_one({"_id":ObjectId(ident)})
        if item is not None:
            await item_collection.delete_one({"_id":ObjectId(ident)})
            return True


class UpdateItemModel(BaseModel):
    name : Optional[str]

    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
    }


