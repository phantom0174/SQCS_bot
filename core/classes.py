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
        self.link_dict = {
            "sta": str(os.environ.get("StaticSettingJson")),
            "dyn": str(os.environ.get("DynamicSettingJson")),
            "human": str(os.environ.get("HumanityExtensionJson"))
        }

    def get_json(self, type):
        if type not in self.link_dict.keys():
            error_json = {
                "type": "get_json_error"
            }
            return error_json

        response = requests.get(self.link_header, {
            "id": self.link_dict[type]
        })
        return response.json()

    def put_json(self, type, alter_json):
        if type not in self.link_dict.keys():
            error_json = {
                "type": "put_json_error"
            }
            return error_json

        update = requests.put(self.link_header,
            params={"id": self.link_dict[type]},
            json=alter_json
        )
