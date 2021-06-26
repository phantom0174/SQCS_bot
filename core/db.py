from pymongo import MongoClient
import os
import requests
from typing import Union

# database
account = os.environ.get("MONGODB_ACCOUNT")
password = os.environ.get("MONGODB_PASSWORD")
link = f"mongodb+srv://{account}:{password}@light-cube-cluster.5wswq.mongodb.net/sqcs?retryWrites=true&w=majority"

# set client
self_client = MongoClient(link)["sqcs-bot"]
fluctlight_client = MongoClient(link)["LightCube"]


class JsonApi:
    def __init__(self):
        self.link_header = 'https://api.jsonstorage.net/v1/json/'

        # json link switcher
        self.json_links = str(os.environ.get("JSON_API_ADAPTER_LINK"))
        self.link_dict = requests.get(self.link_header + self.json_links).json()['links']

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


async def huma_get(directory: str, ending: str = '') -> Union[str, list]:
    dir_split = directory.split('/')

    data = rsp
    for dirs in dir_split:
        if isinstance(data, dict):
            data = data.get(dirs)
        elif isinstance(data, list):
            data = data[int(dirs)]

    if isinstance(data, str):
        return data
    if isinstance(data, list):
        return '\n'.join(data) + ending
