import urllib.request
import urllib.parse
import urllib.error
import aiohttp
import asyncio
import time

from flohmarkt.config import cfg
from flohmarkt.http import HttpClient
from flohmarkt.models.instance_settings import InstanceSettingsSchema

db_url = urllib.parse.urlparse(cfg["Database"]["Server"])
hostname = db_url.netloc.split("@")[1]
probe_url = f"{db_url.scheme}://{hostname}"
while True:
    try:
        print(f"Attempting to connect to DB at: {probe_url}")
        req = urllib.request.Request(probe_url)
        pass #res = urllib.request.urlopen(req, timeout=10)
    except urllib.error.URLError as e:
        print("Failed attempt: "+str(e))
        time.sleep(0.2)
    else:
        break

async def generate_searchvectors():
    while True:
        print("serch")
        await asyncio.sleep(4)

async def get_remote_outbox(instance):
    return #TODO: remove
    print(instance)
    async with HttpClient().get(instance+"/outbox", headers = {
            "Accept":"application/json"
        }) as resp:
        print( await resp.json())

async def get_remote_postings():
    while True:
        try:
            instance_settings = await InstanceSettingsSchema.retrieve()
        except:
            print("Couldn't find instance settings")
        else:
            tasks = []
            for instance in instance_settings["following"]:
                tasks.append(asyncio.create_task(get_remote_outbox(instance)))

            await asyncio.gather(*tasks)
        finally:
            await asyncio.sleep(1)

async def main():
    await HttpClient.initialize()
    t1 = asyncio.create_task(get_remote_postings())
    t2 = asyncio.create_task(generate_searchvectors())
    await t1, t2

if __name__ == "__main__":
    asyncio.run(main())
