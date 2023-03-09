from  motor import motor_asyncio
client = motor_asyncio.AsyncIOMotorClient("mongodb://192.168.0.52:27017")
db = client.flohmarkt

def rename_id(d: dict) -> dict:
    r = {}
    for k,v in d.items():
        if k == "_id":
            r["id"] = str(v)
        else:
            r[k] = v
    return r
