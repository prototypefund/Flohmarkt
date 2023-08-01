import asyncio

class Socketpool():
    NAME_MAP = {}
    URL_MAP = {}
    ID_MAP = {}

    @classmethod
    def add_socket(cls, user, socket):
        cls.NAME_MAP[user["name"]] = socket
        cls.URL_MAP[user["remote_url"]] = socket
        cls.ID_MAP[user["id"]] = socket

    @classmethod
    def get_socket(cls, selector):
        if selector in cls.NAME_MAP:
            return cls.NAME_MAP[selector]
        if selector in cls.ID_MAP:
            return cls.ID_MAP[selector]
        return cls.URL_MAP.get(selector, None)

    @classmethod
    async def shutdown(cls):
        sockets = set()
        for s in cls.NAME_MAP.values():
            sockets.add(s)
        for s in cls.URL_MAP.values():
            sockets.add(s)
        for s in cls.ID_MAP.values():
            sockets.add(s)

        tasks = [s.close() for s in sockets]
        await asyncio.gather(*tasks)

    @classmethod
    async def send_message(cls, message):
        for rcv in message["to"]:
            s = cls.get_socket(rcv)
            if s is None:
                continue
            await s.send_json(message)

    @classmethod
    async def send_conversation(cls, convo):
        s = cls.get_socket(convo["user_id"])
        await s.send_json(convo)
        s = cls.get_socket(convo["remote_user"])
        await s.send_json(convo)
