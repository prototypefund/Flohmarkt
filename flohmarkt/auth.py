import os
import jwt
import json
import datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from flohmarkt.config import cfg
from flohmarkt.models.user import UserSchema

oauth2 = OAuth2PasswordBearer(tokenUrl="token")
oauth2_optional = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

token_blacklist = []
blacklistpath = os.path.join(cfg["General"]["DataPath"], "tokenblacklist.json")
if os.path.exists(blacklistpath):
    blacklistfile = open(blacklistpath,"r")
    for token in json.loads(blacklistfile.read()):
        token_blacklist.append(token)
    blacklistfile.close()

def update_token_blacklist(token):
    """
        Add a new token to the token blacklist and remove any that
        are older than the expiration time
    """
    token_blacklist.append(token)
    for token in token_blacklist:
        diff = datetime.datetime.now() - datetime.datetime.fromtimestamp(token["exp"])
        if diff > datetime.timedelta(days=1):
            token_blacklist.remove(token)
    blacklistfile = open(os.path.join(cfg["General"]["DataPath"], "tokenblacklist.json"),"w")
    blacklistfile.write(json.dumps(token_blacklist))
    blacklistfile.close()

async def get_current_user(token : str = Depends(oauth2)):
    try:
        dec = jwt.decode(token, cfg["General"]["JwtSecret"], algorithms=["HS512"])
        if dec in token_blacklist:
            raise HTTPException(status_code=401, detail="Token blacklisted due to logout")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
    else:
        return await UserSchema.retrieve_single_id(dec["user_id"])

async def get_optional_current_user(token : str = Depends(oauth2_optional)):
    try:
        dec = jwt.decode(token, cfg["General"]["JwtSecret"], algorithms=["HS512"])
        if dec in token_blacklist:
            raise HTTPException(status_code=401, detail="Token blacklisted due to logout")
    except Exception as e:
        return None
    else:
        return await UserSchema.retrieve_single_id(dec["user_id"])

async def blacklist_token(token : str = Depends(oauth2)):
    try:
        dec = jwt.decode(token, cfg["General"]["JwtSecret"], algorithms=["HS512"])
        update_token_blacklist(dec)
    except Exception as e:
        print(e)
    return True
