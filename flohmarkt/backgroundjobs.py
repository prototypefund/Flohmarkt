import asyncio

from flohmarkt.config import cfg
from flohmarkt.db import Database

import os

async def clean_images():
    await asyncio.sleep(10) # dont interrupt the first requests to the other routes
    print("Cleaning up unused images")

    fs_images = os.listdir(os.path.join(cfg["General"]["DataPath"], "images")) 

    item_images = await Database.find({
        "type": "item",
    }, fields=["images"])

    avatar_images = await Database.find({
        "type": "user",
    }, fields=["avatar"])

    item_images = [i["images"] for i in item_images]
    avatar_images = [a["avatar"] for a in avatar_images]

    imagelist = []
    for i in item_images:
        imagelist.extend(i)

    images = []

    images.extend([i["image_id"] for i in imagelist])
    images.extend(avatar_images)

    images_to_delete = set(fs_images) - set(images)

    for image in images_to_delete:
        path = os.path.join(cfg["General"]["DataPath"], "images", image)
        print (f"Deleting {path}")
        os.unlink(path)

    await asyncio.sleep(1*60*60)
    mainloop = asyncio.get_running_loop()
    mainloop.create_task(background_task())
