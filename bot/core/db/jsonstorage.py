import os
import requests

# JsonApi semi-database

link_header = 'https://api.jsonstorage.net/v1/json/'

# json link switcher
json_links = str(os.environ.get("JSON_API_ADAPTER_LINK"))
link_dict = requests.get(link_header + json_links).json()['links']


class JsonApi:
    @staticmethod
    def reload_switcher():
        global link_dict
        link_dict = requests.get(link_header + json_links).json()['links']

    @staticmethod
    def get(name):
        if name not in link_dict.keys():
            return None

        response = requests.get(link_header + link_dict[name])
        return response.json()

    @staticmethod
    def put(name, alter_json):
        if name not in link_dict.keys():
            return None

        return requests.put(link_header + link_dict[name], json=alter_json)

    # humanity extension parser
    @staticmethod
    async def get_humanity(directory: str, ending: str = '') -> str:
        rsp = JsonApi.get('HumanityExtension')

        dir_split = directory.split('/')

        for dirs in dir_split:
            if isinstance(rsp, dict):
                rsp = rsp.get(dirs)
            elif isinstance(rsp, list):
                rsp = rsp[int(dirs)]

        if isinstance(rsp, str):
            return rsp
        if isinstance(rsp, list):
            return '\n'.join(rsp) + ending
