import uuid
import json
import asyncio
import urllib.parse

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
        doc = await cls.find_one(ident)
        uuid = ident["id"]
        rev = doc["_rev"]
        url = cfg["Database"]["Server"]+f"flohmarkt/{uuid}?rev={rev}"
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
        if len(o.keys()) == 1 and list(o.keys())[0] in ("id","_id"):
            if "id" in o:
                o["_id"] = o["id"]
                del(o["id"])
            url = cfg["Database"]["Server"]+f"flohmarkt/{o['_id']}"
            async with HttpClient().get(url, headers = {"Content-type": "application/json"}) as resp:
                res = await resp.json()
                if resp.status == 404:
                    print(res)
                    return
                else:
                    return res
        res = await cls.find(o)
        if len(res) > 1:
            raise Exception("More than one object")
        elif len(res) == 1:
            return res[0]
        else:
            return None

    @classmethod
    async def view(cls, ddoc, view, key=None, group_level:int=None, reduce:bool=None, include_docs:bool = None):
        url = cfg["Database"]["Server"]+f"flohmarkt/_design/{ddoc}/_view/{view}?"

        if type(key) == str:
            url += f"key=%22{key}%22&"
        elif type(key) == list:
            url += f"keys="+urllib.parse.quote(json.dumps(key))+"&"

        if group_level is not None:
            url += f"group_level={group_level}&"

        if reduce is not None:
            url += "reduce=" + ("false", "true")[int(reduce)]

        if include_docs is not None:
            url += "include_docs=" + ("False", "True")[int(include_docs)]

        try:
            async with HttpClient().get(url, headers={"Content-type": "application/json"}) as resp:
                res = await resp.json()
                if resp.status == 400:
                    print(res)
                else:
                    return res['rows']
        except asyncio.exceptions.TimeoutError:
            raise Exception("HTTP TIMEOUT DATABASE")
        except Exception as e:
            raise(e)
