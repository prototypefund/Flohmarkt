import sys
import base64
import json
import urllib.request
import urllib.parse
import urllib.error


from flohmarkt.config import cfg

class PutRequest(urllib.request.Request):
    def get_method(self, *args, **kwargs):
        return 'PUT'

if len(sys.argv) != 3:
    print("Please supply the admin password  and the user password as argument")
    sys.exit(1)
admin_pw = sys.argv[1]
user_pw = sys.argv[2]

raw_url = cfg["Database"]["Server"]
if not ":" in raw_url or not "@" in raw_url:
    print("No credentials in DB server url")
    sys.exit(1)

db_url = urllib.parse.urlparse(cfg["Database"]["Server"])
hostname = db_url.netloc.split("@")[1]
credentials = f"admin:{admin_pw}"
credentials = (base64.b64encode(credentials.encode('utf-8'))).decode()

print("Trying to create user DB")
req = PutRequest(f"{db_url.scheme}://{hostname}/_users")
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
try:
    res = urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    if "412" in str(e):
        print ("Database exists, skipping")
    else:
        print(e)

print("Trying to create flohmarkt DB")
req = PutRequest(f"{db_url.scheme}://{hostname}/flohmarkt")
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
try:
    res = urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    if "412" in str(e):
        print ("Database exists, skipping")
    else:
        print(e)

print("Trying to add flohmarkt User")
req = PutRequest(f"{db_url.scheme}://{hostname}/_users/org.couchdb.user:flohmarkt")
req.data = json.dumps({
    "_id": "org.couchdb.user:flohmarkt",
    "name": "flohmarkt",
    "type": "user",
    "roles": [],
    "password": user_pw
}).encode('utf-8')
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
try:
    res = urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    if "409" in str(e):
        print ("User flohmarkt exists. skipping")
    else:
        print(e)

print("Allow user to write database")
req = PutRequest(f"{db_url.scheme}://{hostname}/flohmarkt/_security")
req.data = json.dumps({
    "writers": {
        "names":["flohmarkt"],
        "roles":["editor"]
    }
}).encode('utf-8')
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
res = urllib.request.urlopen(req)

print("Trying to add date search index")
req = urllib.request.Request(f"{db_url.scheme}://{hostname}/flohmarkt/_index")
req.data = json.dumps({
    "ddoc": "text-index",
    "index": {
        "fields": [{
             "creation_date":"desc"
        }]
    },
    "name": "sort_creation_date",
    "type": "json"
}).encode('utf-8')
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
res = urllib.request.urlopen(req)


