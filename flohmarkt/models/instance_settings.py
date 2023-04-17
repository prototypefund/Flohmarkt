from typing import Optional, List
from pydantic import BaseModel, Field

from flohmarkt.db import Database

class InstanceSettingsSchema(BaseModel):
    id : str = "instance_settings"
    type : str = "instance_settings"
    rules : str = ""
    about : str = ""
    coordinates : str = Field(...)
    range : str = Field(...)
    following : List[str] = []
    followers : List[str] = []
    
    class Config: 
        schema_extra = {
            "example": {
                "rules": "be excellent to each other",
                "about": "my little instance for my little town",
                "coordinates": "49.80:9.90",
                "range": 50,
                "followers": ["https://other.flohmarkt.instance.org"],
                "following": ["https://other.flohmarkt.instance.org"],
            }
        }
    @staticmethod
    async def retrieve():
        return await Database.find_one({"type":"instance_settings", "id":"instance_settings"})

    @staticmethod
    async def set(data: dict):
        data["id"] = "instance_settings"
        data["type"] = "instance_settings"

        updated = await Database.update(
            user_to_activate["id"], user_to_activate
        )
        return True

        ins = await Database.create(data)
        new = await Database.find_one({"id":ins})
        return new

class UpdateInstanceSettingsModel(BaseModel):
    name: Optional[str]
    about: Optional[str]
    rules: Optional[str]
    coordinates: Optional[str]
    perimeter: Optional[int]

    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
    }

