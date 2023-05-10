import aiohttp
import asyncio

async def generate_searchvectors():
    while True:
        print("serch")
        await asyncio.sleep(4)

async def get_remote_postings():
    while True:
        print("LOL")
        await asyncio.sleep(1)

async def main():
    t1 = asyncio.create_task(get_remote_postings())
    t2 = asyncio.create_task(generate_searchvectors())
    await t1, t2

if __name__ == "__main__":
    asyncio.run(main())
