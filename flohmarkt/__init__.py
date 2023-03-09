
from fastapi import FastAPI

from flohmarkt.routes.item import router as item_router

app = FastAPI()
app.include_router(item_router, tags=["Item"], prefix="/item")

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

