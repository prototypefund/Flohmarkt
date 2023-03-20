import aiohttp
import asyncio

from flohmarkt.ssl import ssl_context

class HttpClient():
    CS = None
    TIMEOUT = 1
    INITIALIZED = False

    @classmethod
    async def initialize(cls):
        conn = aiohttp.TCPConnector(ssl_context=ssl_context)
        cls.CS = aiohttp.ClientSession(
            connector = conn,
            headers = {
                "User-Agent": "Flohmarkt Server (python3 + aiohttp)"
            },
            timeout = aiohttp.ClientTimeout(
                total = 10,
                connect = 5,
                sock_connect = 5,
                sock_read = 10 
            )
        )
        cls.INITIALIZED = True

    @classmethod
    async def shutdown(cls):
        await cls.CS.close()

    def __new__(cls):
        if not cls.INITIALIZED:
            raise Exception("HTTP Client not initialized. Aborting…")
        return cls.CS

