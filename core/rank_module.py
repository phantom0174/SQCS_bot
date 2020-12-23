import math
import core.functions as func
from core.setup import jdata, client, link
from pymongo import MongoClient
import discord


async def get_rank(bot, score, new_mode):
    member_count = bot.guilds[0].member_count
    rank_gap = 5 * pow(member_count, 1 / 3)

    rank_index = int(score / rank_gap)

    mvisualizer_client = MongoClient(link)["mvisualizer"]
    rank_cursor = mvisualizer_client["rank_index"]

    data = rank_cursor.find({"_id": new_mode + rank_index})
    new_rank = data["name"]

    return new_rank
