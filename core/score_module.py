import math
import core.functions as func
from core.setup import jdata, client, link
from pymongo import MongoClient
import core.rank_module as rk_mod
import discord
import asyncio


async def active_log_update(bot, member_id):
    fluctlight_client = MongoClient(link)["LightCube"]
    fluctlight_cursor = fluctlight_client["light-cube-info"]

    # week active update
    data = fluctlight_cursor.find_one({"_id": member_id}, {"week_active": 1})
    if data["week_active"] == 0:
        fluctlight_cursor.update_one({"_id": member_id}, {"$set": {"week_active": 1}})
