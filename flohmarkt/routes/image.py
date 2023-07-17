import os
import uuid
import base64

import magic
if hasattr(magic, "compat"):
    import magic.compat as magic

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from flohmarkt.models.user import UserSchema, UpdateUserModel
from flohmarkt.auth import oauth2, get_current_user
from flohmarkt.config import cfg

router = APIRouter()

m = magic.open(magic.MAGIC_MIME)
m.load()

async def assert_imagepath():
    imagepath = os.path.join(cfg["General"]["DataPath"], "images")
    if not os.path.exists(imagepath):
        os.mkdir(imagepath)

@router.post("/", response_description="Image upload")
async def upload_image(current_user : UserSchema = Depends(get_current_user), image: bytes = Body(...)):
    await assert_imagepath()
    users = await UserSchema.retrieve()
    if image.startswith(b"data:"):
        image = image.split(b",")[1]
        image = base64.b64decode(image)

    image_id = str(uuid.uuid4())

    path = os.path.join(cfg["General"]["DataPath"], "images", image_id)

    imagefile = open(path, "wb")
    imagefile.write(image)
    imagefile.close()

    print(path)

    mime = m.file(path).split(";")[0]

    print(mime)
    if not mime.startswith("image/"):
        os.unlink(path)
        raise HTTPException(status_code=400, detail="This mimetype is in an unacceptable condition. UNACCEPTABLE!1!!1")

    return image_id

@router.get("/{ident}", response_description="Get an image")
async def get_image(ident: str):
    await assert_imagepath()
    path = os.path.join(cfg["General"]["DataPath"], "images", ident)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found :(")
    imagefile = open(path, "rb")
    data = imagefile.read()
    imagefile.close()

    mime = m.file(path).split(";")[0]

    print(mime[0])

    response = StreamingResponse(iter([data]),
        media_type=mime
    )

    #response.headers["Content-Disposition"] = "attachment; filename="+ident+"."+ext

    return response
