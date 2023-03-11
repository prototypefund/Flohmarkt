from  motor import motor_asyncio

from flohmarkt.config import cfg

db_server = cfg["Database"]["Server"]
db_port = cfg["Database"]["Port"]

client = motor_asyncio.AsyncIOMotorClient(f"mongodb://{db_server}:{db_port}")
db = client.flohmarkt

def rename_id(d: dict) -> dict:
    r = {}
    for k,v in d.items():
        if k == "_id":
            r["id"] = str(v)
        else:
            r[k] = v
    return r
