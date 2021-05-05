from pymongo import MongoClient
import os
from core.cog_config import JsonApi


# database
password = os.environ.get("PW")
account = os.environ.get("ACCOUNT")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"

fluctlight_client = MongoClient(link)["LightCube"]
self_client = MongoClient(link)["sqcs-bot"]

# static json db
rsp = JsonApi().get_json('HumanityExtension')
