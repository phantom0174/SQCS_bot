import math
import core.functions as func
from core.setup import jdata, client, link
from pymongo import MongoClient
import discord
import asyncio


async def rank_update(bot, member_id):
    synthesizer_client = MongoClient(link)["synthesizer"]
    player_info_cursor = synthesizer_client["player-info"]
    fluctlight_cursor = client["light-cube-info"]

    data = player_info_cursor.find_one({"_id": member_id})

    if data is None:
        return

    old_rank = data["rank"]
    old_mode = old_rank[0]

    # check if member needs path selection
    # If yes, return new selected path and role-name
    # If not, return old path and role-name

    # check if member need path selection
    data = fluctlight_cursor.find_one({"_id": member_id}, {"score": 1})

    new_mode = str()
    if data["score"] >= 500 and old_mode == 'n':
        new_mode = new_mode_select(bot, member_id)

    if new_mode == 'e':
        return

    new_rank = await get_rank(bot, data["score"], new_mode)

    if new_rank != old_rank:
        player_info_cursor.update_one({"_id": member_id}, {"$set": {"rank": new_rank}})
        if old_mode != new_mode:
            player_info_cursor.update_one({"_id": member_id}, {"$set": {"mode": new_mode}})
        member = await bot.fetch_user(member_id)
        await member.send(f'你進階到了 {new_rank}!')


async def new_mode_select(bot, member_id):
    def check(message):
        return message.channel == member.dm_channel and message.author == member

    member = bot.fetch_user(member_id)
    await member.send('Which kind of occupation do you want to take?\n'
                      'Type \"oc\" for melee, and \"sc\" for system.')

    try:
        answer_mode = (await bot.wait_for('message', check=check, timeout=30.0)).content
        if answer_mode != 'oc' or answer_mode != 'sc':
            return 'e'

        return answer_mode
    except asyncio.TimeoutError:
        return 'e'


async def get_rank(bot, score, new_mode):
    member_count = bot.guilds[0].member_count
    rank_gap = 5 * pow(member_count, 1 / 3)

    rank_index = int(score / rank_gap)

    mvisualizer_client = MongoClient(link)["mvisualizer"]
    rank_cursor = mvisualizer_client["rank_index"]

    new_rank = rank_cursor.find_one({"_id": new_mode + rank_index})["name"]

    return new_rank
