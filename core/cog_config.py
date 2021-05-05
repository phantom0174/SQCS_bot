from discord.ext import commands
import os
import requests
from core.db import fluctlight_client
from core.utils import DiscordExt


class CogExtension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


class JsonApi:
    def __init__(self):
        self.link_header = 'https://api.jsonstorage.net/v1/json/'

        # json link switcher
        self.json_links = str(os.environ.get("JsonApiLinks"))
        self.link_dict = requests.get(self.link_header + self.json_links).json()["links"]

    def get_json(self, name):
        if name not in self.link_dict.keys():
            return None

        response = requests.get(self.link_header + self.link_dict[name])
        return response.json()

    def put_json(self, name, alter_json):
        if name not in self.link_dict.keys():
            return None

        requests.put(self.link_header + self.link_dict[name], json=alter_json)


class Fluct:
    def __init__(self, member_id=None):
        self.main_fluct_cursor = fluctlight_client["MainFluctlights"]
        self.vice_fluct_cursor = fluctlight_client["ViceFluctlights"]
        self.act_cursor = fluctlight_client["active-logs"]

        if member_id is not None:
            self.member_fluctlight = self.main_fluct_cursor.find_one({"_id": member_id})

    async def reset_main(self, member_id, guild):
        default_main_fluctlight = {
            "_id": member_id,
            "name": await DiscordExt.get_member_nick_name(guild, member_id),
            "score": 0,
            "week_active": False,
            "contrib": 0,
            "lvl_ind": 0,
            "deep_freeze": False
        }
        try:
            self.main_fluct_cursor.delete_one({"_id": member_id})
        except:
            pass

        try:
            self.main_fluct_cursor.insert_one(default_main_fluctlight)
        except:
            pass

    async def reset_vice(self, member_id):
        default_vice_fluctlight = {
            "_id": member_id,
            "du": 0,
            "mdu": 0,
            "oc_auth": 0,
            "sc_auth": 0,
        }
        try:
            self.vice_fluct_cursor.delete_one({"_id": member_id})
        except:
            pass

        try:
            self.vice_fluct_cursor.insert_one(default_vice_fluctlight)
        except:
            pass

    async def reset_active(self, member_id):
        default_act = {
            "_id": member_id,
            "log": ''
        }
        try:
            self.act_cursor.delete_one({"_id": member_id})
        except:
            pass

        try:
            self.act_cursor.insert_one(default_act)
        except:
            pass
