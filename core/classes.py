import discord
from discord.ext import commands
import os
import requests


class Cog_Extension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class JsonApi:
    def __init__(self):
        self.link_header = 'https://api.jsonstorage.net/v1/json/'

        self.abbreviation_dict = {
            "sta": "StaticSettingJson",
            "dyn": "DynamicSettingJson",
            "hum": "HumanityExtensionJson",
            "nt": "NTJson"
        }

        # json link switcher
        self.json_links = str(os.environ.get("JsonApiLinks"))
        self.link_dict = requests.get(self.link_header + self.json_links).json()

    def get_json(self, name):
        if name not in self.abbreviation_dict.keys():
            error_json = {"type": "get_json_error"}
            return error_json

        full_name = self.abbreviation_dict[name]
        response = requests.get(self.link_header + self.link_dict[full_name])
        return response.json()

    def put_json(self, name, alter_json):
        if name not in self.abbreviation_dict.keys():
            error_json = {"type": "put_json_error"}
            return error_json

        full_name = self.abbreviation_dict[name]
        update = requests.put(self.link_header + self.link_dict[full_name], json=alter_json)
