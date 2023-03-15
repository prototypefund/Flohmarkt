import jwt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from flohmarkt.config import cfg
from flohmarkt.models.user import UserSchema

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token : str = Depends(oauth2)):
    try:
        dec = jwt.decode(token, cfg["General"]["JwtSecret"], algorithms=["HS512"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    else:
        return await UserSchema.retrieve_single_id(dec["user_id"])
