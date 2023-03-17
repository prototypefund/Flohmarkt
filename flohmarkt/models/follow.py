from typing import Optional
from pydantic import BaseModel, Field

class FollowSchema(BaseModel):
    context : str = Field(..., alias="@context")
    id : str = Field(...)
    type : str = Field(...)
    actor : str = Field(...)
    object : str = Field(...)
    
    class Config: 
        schema_extra = {
            "example": {
                "name": "horst schlüter",
                "email": "horst@schlueter.de",
                "pwhash": "$2$fjweöklfjwelkfjweöfkwefölwekjfewf",
            }
        }
"""
Mar 17 19:42:39 testcontainer flohmarkt-start[401]: {'@context': 'https://www.w3.org/ns/activitystreams', 'id': 'https://mastodont.lan/d40547cf-bce1-4393-91f4-07eea0f4d314', 'type': 'Follow', 'actor': 'https://mastodont.lan/users/grindhold', 'object': 'https://testcontainer.lan/users/grindolite'}
Mar 17 19:42:39 testcontainer flohmarkt-start[401]: INFO:     192.168.0.55:0 - "POST /users/grindolite/inbox HTTP/1.1" 200 OK
"""
