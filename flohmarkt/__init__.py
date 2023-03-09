
from fastapi import FastAPI
from  motor import motor_asyncio
from pydantic import BaseModel

import models

app = FastAPI()
client = motor_asyncio.AsyncIOMotorClient("192.168.1.52:27017")
db = client.flohmarkt

@app.on_event("startup")
async def ini():
    print ("hamlo i bims 1 api")
@app.get("/")
async def root():
    return {"message": "Hello World"}
@app.get("/test")
async def other():
    return {"message": "deinemamalel"}

@app.get("/toast/{toast_id}")
async def other(toast_id:int):
    return {"message": "1 toast"}

