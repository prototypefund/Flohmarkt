import asyncio

from flohmarkt.config import cfg
from flohmarkt.db import Database

import os

async def clean_images():
    await asyncio.sleep(10) # dont interrupt the first requests to the other routes
    print("Cleaning up unused images")

    imagespath = os.path.join(cfg["General"]["DataPath"], "images")
    if not os.path.exists(imagespath): # on spawn a image folder may not exist yet
        return
    fs_images = os.listdir(imagespath) 

    item_images = []
    item_image_batch = None
    limit = 100
    skip = 0

    while item_image_batch != []:
        item_image_batch = await Database.find({
            "type": "item",
        }, fields=["images"], limit=limit, skip=skip)
        limit += 100
        skip += 100
        item_images.extend(item_image_batch)

    avatar_images = []
    avatar_image_batch = None
    limit = 100
    skip = 0

    while avatar_image_batch != []:
        avatar_image_batch = await Database.find({
            "type": "user",
        }, fields=["avatar"], limit=limit, skip=skip)
        limit += 100
        skip += 100
        avatar_images.extend(avatar_image_batch)

    item_images = [i["images"] for i in item_images]
    avatar_images = [a["avatar"] for a in avatar_images if a is not None]

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
    mainloop.create_task(clean_images())
