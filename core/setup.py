import json
import pymongo
from pymongo import MongoClient
import os
from core.classes import JsonApi


# database setup
password = os.environ.get("PW")
account = os.environ.get("ACCOUNT")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"
client = MongoClient(link)["sqcs-bot"]
fluctlight_client = MongoClient(link)["LightCube"]

rsp = JsonApi().get_json('HumanityExtensionJson')

