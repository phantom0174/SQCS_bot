import math
import core.functions as func
from core.setup import jdata, client, link
from pymongo import MongoClient
import core.rank_module as rk_mod
import discord
import asyncio


# a full integration of updating member's score-related attributes
async def score_related_attribute_update(bot, member_id):
    fluctlight_client = MongoClient(link)["LightCube"]
    fluctlight_cursor = fluctlight_client["light-cube-info"]

    # week active update
    data = fluctlight_cursor.find_one({"_id": member_id}, {"week_active": 1})
    if data["week_active"] == 0:
        fluctlight_cursor.update_one({"_id": member_id}, {"$set": {"week_active": 1}})

    # rank update
    player_info_cursor = fluctlight_client["player-info"]

    data = player_info_cursor.find_one({"_id": member_id})
    old_rank = data["rank"]
    old_mode = data["rank_mode"]

    # rank path classifier
    data = fluctlight_cursor.find_one({"_id": member_id}, {"score": 1})

    new_mode = str()
    if data["score"] >= 500 and old_mode == 1:
        new_mode = new_mode_select(bot, member_id)

    if new_mode == '-1':
        return

    if new_mode == '':
        new_mode = '0'

    new_rank = rk_mod.get_rank(bot, data["score"], new_mode)

    if new_rank != old_rank:
        player_info_cursor.update_one({"_id": member_id}, {"$set": {"rank": new_rank}})
        if old_mode != new_mode:
            player_info_cursor.update_one({"_id": member_id}, {"$set": {"mode": new_mode}})
        member = await bot.fetch_user(member_id)
        await member.send(f'你進階到了 {new_rank}!')


async def new_mode_select(bot, member_id):
    def check(message):
        return message.channel == member.dm_channel and message.author == member

    member = await bot.fetch_user(member_id)
    await member.send('Which kind of occupation do you want to take?\n'
                      'Type \"2\" for melee, and \"3\" for system.')

    try:
        answer_mode = (await bot.wait_for('message', check=check, timeout=30.0)).content
        if answer_mode != '2' or answer_mode != '3':
            return '-1'

        return answer_mode
    except asyncio.TimeoutError:
        return '-1'
