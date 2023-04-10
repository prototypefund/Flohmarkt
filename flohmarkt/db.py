import uuid
import json
import asyncio

from fastapi.encoders import jsonable_encoder

from flohmarkt.config import cfg
from flohmarkt.http import HttpClient

db_server = cfg["Database"]["Server"]

class Database:
    @classmethod
    async def create(cls, o: dict):
        if not "id" in o:
            o["id"] = str(uuid.uuid4())
        url = cfg["Database"]["Server"]+f"flohmarkt/{o['id']}"
        o = jsonable_encoder(o)
        try:
            async with HttpClient().put(url, data=json.dumps(o)) as resp:
                await resp.json()
                return o["id"]
        except asyncio.exceptions.TimeoutError:
            raise Exception("HTTP TIMEOUT DATABASE")
        except Exception as e:
            raise(e)

    @classmethod
    async def update(cls, ident: str, o: dict):
        doc = await cls.find_one({"id":ident})
        o["_rev"] = doc["_rev"]
        url = cfg["Database"]["Server"]+f"flohmarkt/{ident}"
        o = jsonable_encoder(o)
        try:
            async with HttpClient().put(url, data=json.dumps(o)) as resp:
                return await resp.json()
        except asyncio.exceptions.TimeoutError:
            raise Exception("HTTP TIMEOUT DATABASE")
        except Exception as e:
            raise(e)

    @classmethod
    async def delete(cls, ident: str):
        url = cfg["Database"]["Server"]+f"flohmarkt/{ident}"
        try:
            async with HttpClient().delete(url) as resp:
                return await resp.json()
        except asyncio.exceptions.TimeoutError:
            raise Exception("HTTP TIMEOUT DATABASE")
        except Exception as e:
            raise(e)

    @classmethod
    async def find(cls, o: dict, sort: dict = [], limit: int = None):
        url = cfg["Database"]["Server"]+f"flohmarkt/_find"
        o = {"selector":o,
             "sort": sort}
        if limit is not None and type(limit) == int:
            o["limit"] = limit
        o = jsonable_encoder(o)
        try:
            async with HttpClient().post(url, data=json.dumps(o), headers = {"Content-type": "application/json"}) as resp:
                print(resp.status)#.status_code)
                res = await resp.json()
                if resp.status == 400:
                    print(res)
                else:
                    return res['docs']
        except asyncio.exceptions.TimeoutError:
            raise Exception("HTTP TIMEOUT DATABASE")
        except Exception as e:
            raise(e)


    @classmethod
    async def find_one(cls, o: dict):
        res = await cls.find(o)
        if len(res) > 1:
            raise Exception("More than one object")
        elif len(res) == 1:
            return res[0]
        else:
            return None
