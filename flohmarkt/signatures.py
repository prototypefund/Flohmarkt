import base64

from fastapi import Request

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from flohmarkt.http import HttpClient

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
        ret  =[]
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

def sign(req: Request):
    pass #TODO: implement
