import uuid
import json

import aiohttp
import asyncio

from flohmarkt.config import cfg

db_server = cfg["Database"]["Server"]

class Database:
    CS = None
    TIMEOUT = 1

    @classmethod
    async def initialize(cls):
        cls.CS = aiohttp.ClientSession()

    @classmethod
    async def shutdown(cls):
        await cls.CS.close()

    @classmethod
    async def create(cls, o: dict):
        if not "id" in o:
            o["id"] = str(uuid.uuid4())
        url = cfg["Database"]["Server"]+f"flohmarkt/{o['id']}"
        try:
            async with  cls.CS.put(url, data=json.dumps(o), timeout=cls.TIMEOUT
            ) as resp:
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
        try:
            async with  cls.CS.put(url, data=json.dumps(o), timeout=cls.TIMEOUT
            ) as resp:
                return await resp.json()
        except asyncio.exceptions.TimeoutError:
            raise Exception("HTTP TIMEOUT DATABASE")
        except Exception as e:
            raise(e)

    @classmethod
    async def delete(cls, ident: str):
        url = cfg["Database"]["Server"]+f"flohmarkt/{ident}"
        try:
            async with  cls.CS.delete(url, timeout=cls.TIMEOUT
            ) as resp:
                return await resp.json()
        except asyncio.exceptions.TimeoutError:
            raise Exception("HTTP TIMEOUT DATABASE")
        except Exception as e:
            raise(e)

    @classmethod
    async def find(cls, o: dict):
        url = cfg["Database"]["Server"]+f"flohmarkt/_find"
        o = {"selector":o}
        try:
            async with  cls.CS.post(url, data=json.dumps(o), headers = {"Content-type": "application/json"}, timeout=cls.TIMEOUT
            ) as resp:
                res = await resp.json()
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
