import datetime

from typing import Optional, List
from pydantic import BaseModel, Field

try:
    from Crypto.PublicKey import RSA
except ModuleNotFoundError:
    from Cryptodome.PublicKey import RSA
 

from flohmarkt.db import Database
from flohmarkt.models.follow import FollowSchema

class ModeEnum:
    SELL = 0
    GIVEAWAY = 1

USERS_PER_PAGE = 25

class UserSchema(BaseModel):
    id : str = Field(...)
    type : str = Field(...)
    name : str = Field(...)
    email : str = Field(...)
    pwhash : str = Field(...)
    avatar : str = Field(...)
    active : bool = Field(...)
    admin : bool = Field(...)
    private_key : str = Field(...)
    public_key : str = Field(...)
    moderator : bool = Field(...)
    activation_code : str = Field(...)
    banned : bool = False
    reset_token : str = ""
    followers : dict[str, FollowSchema] = {}
    role : str = Field(...)
    remote_url : Optional[str] = None
    watching : list = []
    creation_date : Optional[datetime.datetime] = datetime.datetime.now()
    
    class Config: 
        schema_extra = {
            "example": {
                "name": "horst schlüter",
                "email": "horst@schlueter.de",
                "pwhash": "$2$fjweöklfjwelkfjweöfkwefölwekjfewf",
            }
        }
    @staticmethod
    async def retrieve(skip: int = 0):
        return await Database.find({"type":"user"}, 
                            limit=USERS_PER_PAGE,
                            skip=skip)

    @staticmethod
    async def retrieve_local(skip: int = 0):
        return await Database.find({
                                "type":"user",
                                "name": {"$not": { "$regex":"@"}}
                            }, 
                            limit=USERS_PER_PAGE,
                            skip=skip)

    @staticmethod
    async def retrieve_many(ids: List[str] = []):
        ret = []
        result = await Database.view("many_users", "users-view", key=ids, include_docs=True)
        for row in result:
            ret.append(row["doc"])
        return ret


    @staticmethod
    async def add(data: dict)->dict:
        data["type"] = "user"

        keypair = RSA.generate(2048)
        data["private_key"] = keypair.export_key()
        data["public_key"] = keypair.public_key().export_key()

        ins = await Database.create(data)
        new = await Database.find_one({"id":ins})
        return new

    @staticmethod
    async def activate(code: str)->dict:
        user_to_activate = await Database.find_one({"type":"user","activation_code":code})
        if user_to_activate is None:
            return False

        user_to_activate["active"] = True

        updated = await Database.update(
            user_to_activate["id"], user_to_activate
        )
        return True

    @staticmethod
    async def retrieve_single_id(ident: str)->dict:
        user = await Database.find_one({"id":ident})
        if user is not None:
            return user

    @staticmethod
    async def retrieve_single_name(name: str)->dict:
        user = await Database.find_one({"type":"user", "name":name})
        if user is not None:
            return user

    @staticmethod
    async def retrieve_single_remote_url(remote_url: str)->dict:
        user = await Database.find_one({"type":"user", "remote_url":remote_url})
        if user is not None:
            return user

    @staticmethod
    async def retrieve_single_email(email: str)->dict:
        user = await Database.find_one({"type":"user", "email":email})
        if user is not None:
            return user

    @staticmethod
    async def retrieve_single_resetcode(email: str)->dict:
        user = await Database.find_one({"type":"user", "reset_token":email})
        if user is not None:
            return user

    @staticmethod
    async def retrieve_admins()->list:
        return await Database.find({"type":"user", "admin":True})

    @staticmethod
    async def update(ident: str, data: dict, replace=False):
        if len(data) < 1:
            return False

        user = await Database.find_one({"id":ident})
        if replace:
            user = data
        else:
            user.update(data)
        if user is not None:
            updated = await Database.update(
                    ident, user
            )
            if updated is not None:
                return True
            return False

    @staticmethod
    async def delete(ident : str):
        user = await Database.find_one({"id":ident})
        if user is not None:
            await Database.delete({"id":ident})
            return True

    @staticmethod
    async def filter(user):
        fields_to_ignore = (
            "private_key",
            "pwhash",
            "activation_code"
        )
        for fti in fields_to_ignore:
            if fti in user:
                del(user[fti])


class UpdateUserModel(BaseModel):
    bio: str
    avatar: str

    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
    }

