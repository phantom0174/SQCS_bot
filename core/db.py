from pymongo import MongoClient
import os
import requests
from typing import Union


# database
password = os.environ.get("PW")
account = os.environ.get("ACCOUNT")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"

# set client
self_client = MongoClient(link)["sqcs-bot"]
fluctlight_client = MongoClient(link)["LightCube"]


class JsonApi:
    def __init__(self):
        self.link_header = 'https://api.jsonstorage.net/v1/json/'

        # json link switcher
        self.json_links = str(os.environ.get("JsonApiLinks"))
        self.link_dict = requests.get(self.link_header + self.json_links).json()["links"]

    def get(self, name) -> Union[dict, None]:
        if name not in self.link_dict.keys():
            return None

        response = requests.get(self.link_header + self.link_dict[name])
        return response.json()

    def put(self, name, alter_json) -> None:
        if name not in self.link_dict.keys():
            return None

        requests.put(self.link_header + self.link_dict[name], json=alter_json)


# static json db
rsp = JsonApi().get('HumanityExtension')
