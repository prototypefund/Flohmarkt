from typing import Optional, List
from pydantic import BaseModel, Field

from flohmarkt.db import Database
from flohmarkt.config import cfg

class Coordinates(BaseModel):
    lat: float = 52.00
    lng: float = 13.00

class InstanceSettingsSchema(BaseModel):
    id : str = "instance_settings"
    type : str = "instance_settings"
    rules : str = ""
    about : str = ""
    coordinates : Coordinates = Field(...)
    range : str = Field(...)
    following : List[str] = []
    pending_following : List[str] = []
    followers : List[str] = []
    pending_followers : List[str] = []
    registrations : str = "open"
    
    class Config: 
        schema_extra = {
            "example": {
                "data_privacy": "We take good care of your data",
                "imprint": "This website is operated by Erika Mustermann, Hackerstr. 23, 13337 Leethausen",
                "rules": "be excellent to each other",
                "about": "my little instance for my little town",
                "coordinates": "49.80:9.90",
                "range": 50,
                "followers": ["https://other.flohmarkt.instance.org"],
                "pending_followers": [],
                "following": ["https://other.flohmarkt.instance.org"],
                "pending_following": [],
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
            data["id"], data
        )
        return True

class UpdateInstanceSettingsModel(BaseModel):
    name: Optional[str]
    about: Optional[str]
    rules: Optional[str]
    imprint: Optional[str]
    privacy: Optional[str]
    coordinates: Optional[Coordinates]
    perimeter: Optional[int]
    registrations: Optional[str]

    class Config: 
        schema_extra = {
            "example": {
                "name": "Lawnmower"
            }
    }

async def get_instance_name():
    settings = await InstanceSettingsSchema.retrieve()
    if settings["name"] is not None and settings["name"] != "":
        return settings["name"]
    else:
        return cfg["General"]["InstanceName"]
