import uuid
import datetime

from typing import Optional, List
from pydantic import BaseModel, Field

from flohmarkt.db import Database

class ConversationSchema(BaseModel):
    ident : str
    type : Optional[str]
    user_id : str
    remote_user : str
    item_id : str
    messages : List[dict]
    
    class Config: 
        schema_extra = {
            "example": {
                "id"
                "user_id": "adsfds-asdfasd-aasdfadsf-adsfasdfafdadsf",
                "": "1 €",
                "description": "This mows lawns",
            }
        }
    @staticmethod
    async def retrieve_for_item(item_id:str):
        conversations = []
        for conversation in await Database.find({"type":"conversation", "item_id":item_id}):
            conversations.append(conversation)
        return conversations

    @staticmethod
    async def retrieve_for_id(ident:str):
        res =  await Database.find({"type":"conversation", "id":ident})
        if len(res) > 1:
            raise Exception(f"More than one conversation with id: {ident}")
        elif len(res) == 1:
            return res[0]
        else:
            return None

    @staticmethod
    async def retrieve_for_item_remote_user(item_id:str, remote_user: str):
        conversations = []
        selector = {
            "type":"conversation",
            "item_id":item_id,
            "remote_user":remote_user
        }
        for conversation in await Database.find(selector):
            conversations.append(conversation)
        if len(conversations) == 1:
            return conversations[0]
        elif len(conversations) == 0:
            return None
        else:
            raise Exception(f"Found multiple conversations for {remote_user} on  {item_id}")

    @staticmethod
    async def retrieve_for_message_id(remote_message_id : str):
        conversations = []
        selector = {
            "type":"conversation",
            "messages": {
                "$elemMatch": {
                    "id": remote_message_id
                }
            }
        }
        for conversation in await Database.find(selector):
            conversations.append(conversation)
        if len(conversations) == 1:
            return conversations[0]
        elif len(conversations) == 0:
            return None
        else:
            raise Exception(f"Found multiple conversations for {remote_user} on  {item_id}")

    @staticmethod
    async def update(ident: str, data: dict, replace=False):
        if len(data) < 1:
            return False

        conversation = await Database.find_one({"id":ident})
        data["update_date"] = datetime.datetime.now()
        if replace:
            conversation = data
        else:
            conversation.update(data)
        if conversation is not None:
            updated = await Database.update(
                    ident, data
            )
            if updated is not None:
                return True
            return False

    @staticmethod
    async def add(data: dict)->dict:
        data["type"] = "conversation"
        data["id"] = str(uuid.uuid4())
        data["messages"] = []
        data["creation_date"] = datetime.datetime.now()
        data["update_date"] = datetime.datetime.now()
        ins = await Database.create(data)
        new = await Database.find_one({"id":ins})
        return new

class MessageSchema(BaseModel):
    ident: str
    type: Optional[str]
    date : str
    author: str
    msg: str

