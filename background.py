import aiohttp
import asyncio


from flohmarkt.http import HttpClient
from flohmarkt.models.instance_settings import InstanceSettingsSchema

async def generate_searchvectors():
    while True:
        print("serch")
        await asyncio.sleep(4)

async def get_remote_outbox(instance):
    print(instance)
    async with HttpClient().get(instance+"/outbox", headers = {
            "Accept":"application/json"
        }) as resp:
        print( await resp.json())

async def get_remote_postings():
    while True:
        instance_settings = await InstanceSettingsSchema.retrieve()
        tasks = []
        for instance in instance_settings["following"]:
            tasks.append(asyncio.create_task(get_remote_outbox(instance)))

        await asyncio.gather(*tasks)
        await asyncio.sleep(1)

async def main():
    await HttpClient.initialize()
    t1 = asyncio.create_task(get_remote_postings())
    t2 = asyncio.create_task(generate_searchvectors())
    await t1, t2

if __name__ == "__main__":
    asyncio.run(main())
