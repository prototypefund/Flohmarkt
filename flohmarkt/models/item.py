import uuid
import datetime

from typing import Optional, List
from pydantic import BaseModel, Field

from flohmarkt.db import Database

class ModeEnum:
    SELL = 0
    GIVEAWAY = 1

class ImageSchema(BaseModel):
    image_id : str
    description : str

class ItemSchema(BaseModel):
    type : Optional[str] = "item"
    name : str = Field(...)
    user : Optional[str] = ""
    price : str = Field(...)
    images : List[ImageSchema] = Field(...)
    description : str = Field(...)
    url : Optional[str] = ""
    conversations : Optional[set] = []
    creation_date : Optional[datetime.datetime] = datetime.datetime.now()
    suspended : bool = False
    
    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower",
                "price": "1 €",
                "description": "This mows lawns",
            }
        }
    @staticmethod
    async def retrieve():
        items = []
        for item in await Database.find({"type":"item"}):
            items.append(item)
        return items

    @staticmethod
    async def retrieve_many(ids: List[str] = []):
        ret = []
        result = await Database.view("many_items", "items-view", key=ids, include_docs=True)
        for row in result:
            ret.append(row["doc"])
        return ret

    @staticmethod
    async def add(data: dict, user:dict=None)->dict:
        data["type"] = "item"
        if not "id" in data:
            data["id"] = str(uuid.uuid4())
        if not "creation_date" in data or data["creation_date"] is None:
            data["creation_date"] = datetime.datetime.now()

        if user is not None:
            data["url"] = "/~"+user["name"]+"/"+data["id"]
        ins = await Database.create(data)
        new = await Database.find_one({"id":ins})
        return new

    @staticmethod
    async def retrieve_single_id(ident: str)->dict:
        item = await Database.find_one({"id":ident})
        if item is not None:
            return item

    @staticmethod
    async def retrieve_by_user(userid: str)->dict:
        return await Database.find({"type":"item","user":userid})

    @staticmethod
    async def retrieve_most_contested()->List[dict]:
        item_ids = await Database.view("n_conversations_per_item", "conversations-per-item-index", group_level=1)
        item_ids = sorted(item_ids, key=lambda x: x['value'], reverse=True)
        items = []
        for item_id in item_ids:
            items.append(await ItemSchema.retrieve_single_id(item_id['key']))

        return items

    @staticmethod
    async def search(search:str, skip:int=0)->dict:
        result = await Database.find({"$or": [
            {"type":"item", "name": {"$regex":"(?i)"+search}},
            {"type":"item", "description": {"$regex":"(?i)"+search}}
        ]}, [{"creation_date":"desc"}], limit=120, skip=skip)
        return result

    @staticmethod
    async def retrieve_any(skip:int=0)->dict:
        result = await Database.find(
            {"type":"item"},
            [{"creation_date":"desc"}],
            limit=50, skip=skip
        )
        return result

    @staticmethod
    async def retrieve_newest()->dict:
        return await Database.find({"type":"item"},sort=[{"creation_date":"desc"}], limit=10)
    
    @staticmethod
    async def retrieve_oldest()->dict:
        return await Database.find({"type":"item"},sort=[{"creation_date":"asc"}], limit=10)

    @staticmethod
    async def update(ident: str, data: dict):
        if len(data) < 1:
            return False
        item = await Database.find_one({"id":ident})
        item.update(data)
        if item is not None:
            updated = await Database.update(
                    ident, item
            )
            if updated is not None:
                return True
            return False

    @staticmethod
    async def delete(ident : str):
        item = await Database.find_one({"id":ident})
        if item is not None:
            await Database.delete({"id":ident})
            return True


class UpdateItemModel(BaseModel):
    description : Optional[str]

    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
    }


