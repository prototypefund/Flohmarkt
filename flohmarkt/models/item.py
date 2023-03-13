from typing import Optional
from pydantic import BaseModel, Field

from flohmarkt.db import Database

class ModeEnum:
    SELL = 0
    GIVEAWAY = 1

class ItemSchema(BaseModel):
    name : str = Field(...)
    type : str = Field(...)
    
    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
        }
    @staticmethod
    async def retrieve():
        items = []
        async for item in Database.find({"type":"item"}):
            items.append(rename_id(item))
        return items

    @staticmethod
    async def add(data: dict)->dict:
        data["type"] = "item"
        ins = await Database.insert_one(data)
        new = await Database.find_one({"id":ins})
        return new

    @staticmethod
    async def retrieve_single_id(ident: str)->dict:
        item = await Database.find_one({"id":ident})
        if item is not None:
            return item

    @staticmethod
    async def update(ident: str, data: dict):
        if len(data) < 1:
            return False
        item = await Database.find_one({"id":ident})
        item.update(data)
        if item is not None:
            updated = await Database.update(
                    ident, data
            )
            if updated is not None:
                return True
            return False

    @staticmethod
    async def delete(ident : str):
        item = await Database.find_one({"id":ident})
        if item is not None:
            await Database.delete_one({"id":ident})
            return True


class UpdateItemModel(BaseModel):
    name : Optional[str]

    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
    }


