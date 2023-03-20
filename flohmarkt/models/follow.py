from typing import Optional
from pydantic import BaseModel, Field

class FollowSchema(BaseModel):
    context : str = Field(..., alias="@context")
    id : str = Field(...)
    type : str = Field(...)
    actor : str = Field(...)
    object : str = Field(...)
    
    class Config: 
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "@context": "https://somethingavticitapub.org/schemaversion/blah",
                "id": "https://mein.host/users/japierdolebober#folows/42",
                "type": "Follow",
                "actor":"https://mein.host/users/japierdolebober",
                "object": "https://anderer.host/users/kurwabober" 
            }
        }

class AcceptSchema(BaseModel):
    context : str = Field(..., alias="@context")
    id : str = Field(...)
    type : str = Field(...)
    actor : str = Field(...)
    object : FollowSchema = Field(...)

    class Config: 
        allow_population_by_field_name = True
