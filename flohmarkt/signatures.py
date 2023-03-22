import base64
import json
import datetime
from urllib.parse import urlparse

from fastapi import Request

try:
    from Crypto.Signature import pkcs1_15
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import RSA
except ModuleNotFoundError:
    from Cryptodome.Signature import pkcs1_15
    from Cryptodome.Hash import SHA256
    from Cryptodome.PublicKey import RSA

from flohmarkt.config import cfg
from flohmarkt.http import HttpClient
from flohmarkt.models.user import UserSchema

def to_rfc_2616(date: datetime.datetime) -> str:
    months = {
        1 : "Jan",
        2 : "Feb",
        3 : "Mar",
        4 : "Apr",
        5 : "May",
        6 : "Jun",
        7 : "Jul",
        8 : "Aug",
        9 : "Sep",
        10 : "Oct",
        11 : "Nov",
        12 : "Dec"
    }
    days = {
        0 : "Sun",
        1 : "Mon",
        2 : "Tue",
        3 : "Wed",
        4 : "Thu",
        5 : "Fri",
        6 : "Sat"
    }
    weekday = days[date.weekday()]
    month = months[date.month]
    return f"{weekday}, {date.day} {month} {date.year} {date.hour:02d}:{date.minute:02d}:{date.second:02d} GMT"

class Signature:
    def __init__(self, request):
        self.request = request
        self.key_id = None
        self.algorithm = None
        self.headers= []
        self.signature = None
        for v in self.request.headers["signature"].split(","):
            key, val = v.split("=",1)
            if key == "keyId":
                self.key_id = val.strip('"')
            elif key == "headers":
                val = val.strip('"')
                self.headers = val.split(" ")
            elif key == "algorithm":
                self.algorithm = val
            elif key == "signature":
                self.signature = val
            else:
                print("Unknown signature header content: ",k, v)

    async def _check_bodysum(self):
        given_hash = self.request.headers['digest']
        if given_hash.startswith('SHA-256='):
            given_hash = given_hash.replace('SHA-256=', '', 1)
            body_hash = SHA256.new()
            body_hash.update(await self.request.body())
            body_hash = base64.encodebytes(body_hash.digest()).decode('utf-8')
            return body_hash.strip() == given_hash.strip()
        raise NotImplementedError(f"Hash algorithm not implemented for: {given_hash}")

    def _reconstruct(self):
        ret = []
        for head in self.headers:
            if head == "(request-target)":
                ret.append(
                    "(request-target): "+self.request.method.lower() + " " +  self.request.url.path
                )
            else:
                ret.append(head+": "+self.request.headers[head])
        return "\n".join(ret)

    async def _obtain_pubkey(self):
        url = self.key_id.split("#")[0]
        async with HttpClient().get(url, headers = {
                "Accept":"application/json"
            }) as resp:
            data = await resp.json()
            return RSA.importKey(data['publicKey']['publicKeyPem'])
        raise Exception("Key could not be obtaineD")

    async def verify(self) -> bool:
        if not await self._check_bodysum():
            return False
        h = SHA256.new()
        h.update(bytes(self._reconstruct(),'utf-8'))
        s = pkcs1_15.new(await self._obtain_pubkey())
        try:
            decodedsig = base64.decodebytes(self.signature.encode('utf-8'))
            s.verify(h, decodedsig)
            return True
        except ValueError:
            print ( "Not a valid signature" )
            return False

async def verify(req: Request):
    return await Signature(req).verify()

def sign(method : str, url: str, headers: dict, data: str, user : UserSchema):
    parsed = urlparse(url)
    request_target = method.lower() + " " + parsed.path
    body_hash = SHA256.new()
    body_hash.update(data.encode('utf-8'))
    body_hash = base64.encodebytes(body_hash.digest()).decode('utf-8')
    digest = ("SHA-256="+body_hash).strip()
    headers["Digest"] = digest
    headers["Host"] = parsed.netloc
    headers["Date"] = to_rfc_2616(datetime.datetime.now(datetime.timezone.utc))
    sign_headers = [
        '(request-target)',
        'Host',
        'Date',
        'Digest',
        'Content-Type'
    ]
    ret = []
    for head in sign_headers:
        if head == "(request-target)":
            ret.append(
                "(request-target): "+method.lower() + " " +  parsed.path
            )
        #elif head == "digest":
        #    ret.append(f"digest: {digest}")
        else:
            ret.append(head.lower()+": "+headers[head])
    signature_text = "\n".join(ret)
    signature_hash = SHA256.new()
    signature_hash.update(bytes(signature_text,'utf-8'))
    s = pkcs1_15.new(RSA.importKey(user['private_key']))
    signature = base64.encodebytes(s.sign(signature_hash)).decode('utf-8').replace("\n","")
    externalurl = cfg["General"]["ExternalURL"]
    headers["Signature"] = f'keyId="{externalurl}/users/{user["name"]}#main-key",algorithm="rsa-sha256",headers="(request-target) host date digest content-type",signature="{signature}"'
