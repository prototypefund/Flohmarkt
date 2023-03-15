import jwt

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from flohmarkt.config import cfg

oauth2 = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token : str = Depends(oauth2)):
    x = jwt.decode(token, cfg["General"]["JwtSecret"], algorithms=["HS512"])
    print(x)
