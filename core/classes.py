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

        # json link switcher
        self.json_links = str(os.environ.get("JsonApiLinks"))
        self.link_dict = requests.get(self.link_header + self.json_links).json()

    def get_json(self, name):
        if name not in self.link_dict.keys():
            error_json = {"type": "get_json_error"}
            return error_json

        response = requests.get(self.link_header + self.link_dict[name])
        return response.json()

    def put_json(self, name, alter_json):
        if name not in self.link_dict.keys():
            error_json = {"type": "put_json_error"}
            return error_json

        update = requests.put(self.link_header + self.link_dict[name], json=alter_json)
