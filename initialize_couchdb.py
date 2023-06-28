import sys
import base64
import json
import uuid
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
    res = urllib.request.urlopen(req, timeout=10)
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
    res = urllib.request.urlopen(req, timeout=10)
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
    res = urllib.request.urlopen(req, timeout=10)
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
res = urllib.request.urlopen(req, timeout=10)

def add_index(column, direction):
    print(f"Trying to add {column} search index")
    req = urllib.request.Request(f"{db_url.scheme}://{hostname}/flohmarkt/_index")
    req.data = json.dumps({
        "ddoc": "text-index",
        "index": {
            "fields": [{
                 column:direction
            }]
        },
        "name": column+"-index",
        "type": "json"
    }).encode('utf-8')
    req.headers = {
        "Content-type": "application/json",
        "Authorization": "Basic "+credentials
    }
    res = urllib.request.urlopen(req, timeout=10)

index_cols = [
    ("creation_date", "desc"),
    ("name", "asc"),
    ("description", "asc"),
    ("item_id", "asc"),
    ("remote_url", "asc"),
]

for i in index_cols:
    add_index(*i)




print("Trying to add conversations-per-item view")
req = PutRequest(f"{db_url.scheme}://{hostname}/flohmarkt/_design/n_conversations_per_item")
req.data = json.dumps({
    "_id": "_design/n_conversations_per_item",
    "views": {
        "conversations-per-item-index": {
            "map": "function (doc) {\n  if (doc.type == \"conversation\") {\n    emit(doc.item_id, 1);\n  }\n}",
            "reduce": "_count"
        }
    },
    "language": "javascript"
}).encode('utf-8')
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
try:
    res = urllib.request.urlopen(req, timeout=10)
except urllib.error.HTTPError as e:
    if "409" in str(e):
        print ("User flohmarkt exists. skipping")
    else:
        print(e)

print("Trying to add multiple-items view")
req = PutRequest(f"{db_url.scheme}://{hostname}/flohmarkt/_design/many-items")
req.data = json.dumps({
    "_id": "_design/many_items",
    "views": {
        "items-view": {
            "map": "function (doc) {\n  if (doc.type == \"item\") {\n    emit(doc.item_id, 1);\n  }\n}"
        }
    },
    "language": "javascript"
}).encode('utf-8')
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
try:
    res = urllib.request.urlopen(req, timeout=10)
except urllib.error.HTTPError as e:
    if "409" in str(e):
        print ("User flohmarkt exists. skipping")
    else:
        print(e)

print("Trying to add instance settigs")
req = PutRequest(f"{db_url.scheme}://{hostname}/flohmarkt/instance_settings")
req.data = json.dumps({
    "id": "instance_settings",
    "type": "instance_settings",
    "initialized" : False,
    "initialization_key": str(uuid.uuid4()),
    "name": "A new Flohmarkt instance",
    "about": "Please enter a text about this instance here",
    "rules": "Please enter the instance rules here",
    "perimeter": 50,
    "coordinates": "",
    "followers": [],
    "following": [],
    "pending_followers": [],
    "pending_following": [],
}).encode('utf-8')
req.headers = {
    "Content-type": "application/json",
    "Authorization": "Basic "+credentials
}
try:
    res = urllib.request.urlopen(req, timeout=10)
except urllib.error.HTTPError as e:
    if "409" in str(e):
        print ("Instance settings already exist. skipping")
    else:
        print(e)
