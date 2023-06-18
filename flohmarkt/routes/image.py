import os
import uuid
import base64

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse

from flohmarkt.models.user import UserSchema, UpdateUserModel
from flohmarkt.auth import oauth2, get_current_user
from flohmarkt.config import cfg

router = APIRouter()

@router.post("/", response_description="Image upload")
async def upload_image(current_user : UserSchema = Depends(get_current_user), image: bytes = Body(...)):
    users = await UserSchema.retrieve()
    if image.startswith(b"data:image/jpeg;base64,"):
        image = image.replace(b"data:image/jpeg;base64,",b"")
        image = base64.b64decode(image)

    image_id = str(uuid.uuid4())

    imagefile = open(os.path.join(cfg["General"]["ImagePath"], image_id+".jpg"), "wb")
    imagefile.write(image)
    imagefile.close()

    return image_id

@router.get("/{ident}", response_description="Get an image")
async def get_image(ident: str):
    path = os.path.join(cfg["General"]["ImagePath"],ident+".jpg")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found :(")
    imagefile = open(path, "rb")
    data = imagefile.read()
    imagefile.close()

    response = StreamingResponse(iter([data]),
        media_type="image/jpeg"
    )

    response.headers["Content-Disposition"] = "attachment; filename="+ident+".jpg"

    return response
