from typing import Optional
from pydantic import BaseModel, Field
from bson.objectid import ObjectId

from flohmarkt.db import db, rename_id

user_collection = db.get_collection("users")

class ModeEnum:
    SELL = 0
    GIVEAWAY = 1

class UserSchema(BaseModel):
    name : str = Field(...)
    email : str = Field(...)
    pwhash : str = Field(...)
    avatar : str = Field(...)
    active : bool = Field(...)
    role : str = Field(...)
    
    
    class Config: 
        schema_extra = {
            "example": {
                "name": "horst schlüter",
                "email": "horst@schlueter.de",
                "pwhash": "$2$fjweöklfjwelkfjweöfkwefölwekjfewf",
            }
        }
    @staticmethod
    async def retrieve():
        users = []
        async for user in user_collection.find():
            users.append(rename_id(user))
        return users

    @staticmethod
    async def add(data: dict)->dict:
        ins = await user_collection.insert_one(data)
        new = await user_collection.find_one({"_id":ins.inserted_id})
        print(new)
        return rename_id(new)

    @staticmethod
    async def retrieve_single_id(ident: str)->dict:
        print(ident)
        user = await user_collection.find_one({"_id":ObjectId(ident)})
        if user is not None:
            return rename_id(user)

    @staticmethod
    async def retrieve_single_name(name: str)->dict:
        user = await user_collection.find_one({"name":name})
        if user is not None:
            return rename_id(user)

    @staticmethod
    async def retrieve_single_email(email: str)->dict:
        user = await user_collection.find_one({"email":email})
        if user is not None:
            return rename_id(user)

    @staticmethod
    async def update(ident: str, data: dict):
        if len(data) < 1:
            return False
        user = await user_collection.find_one({"_id":ObjectId(ident)})
        if user is not None:
            updated = await user_collection.update_one(
                    {"_id":ObjectId(ident)}, {"$set": data}
            )
            if updated is not None:
                return True
            return False

    @staticmethod
    async def delete(ident : str):
        user = await user_collection.find_one({"_id":ObjectId(ident)})
        if user is not None:
            await user_collection.delete_one({"_id":ObjectId(ident)})
            return True


class UpdateUserModel(BaseModel):
    name : Optional[str]

    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
    }


