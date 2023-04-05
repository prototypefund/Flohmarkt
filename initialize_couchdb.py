import sys
import base64
import urllib.request
import urllib.parse


from flohmarkt.config import cfg

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


req = urllib.request.Request(f"{db_url.scheme}://{hostname}/_users/")
req.data = """{
    "_id": "org.couchdb.user:flohmarkt",
    "name": "flohmarkt",
    "type": "user",
    "roles": [],
    "password": user_pw
}""".encode('utf-8')
req.headers = {
    "Content-type: application/json",
    "Authorization: Basic "+credentials
}
print(db_url)
res = urllib.request.urlopen(req)
print(res)


req = urllib.request.Request(f"{db_url.scheme}://{hostname}/flohmarkt/_index")
req.data = """{
    "ddoc": "text-index",
    "index": {
        "fields": [{
             "creation_date":"desc"
        }]
    },
    "name": "sort_creation_date",
    "type": "json"
}""".encode('utf-8')
req.headers = {
    "Content-type: application/json",
    "Authorization: Basic "+credentials
}
res = urllib.request.urlopen(req)
print(res)


