from pymongo import MongoClient
from core.setup import jdata, client, link, fluctlight_client
import core.functions as func
import statistics
import discord


# main function

async def guild_weekly_update(bot):

    # ------------------------------
    # Very important update function
    # ------------------------------

    # set-up client
    fluctlight_cursor = fluctlight_client["light-cube-info"]
    score_parameters_cursor = client["score_parameters"]
    active_logs_cursor = client["active-logs"]

    # calculate total score, max, min score
    max_score = fluctlight_cursor.find_one({}, {"score": 1}, sort=[("score", -1)])["score"]
    min_score = fluctlight_cursor.find_one({}, {"score": 1}, sort=[("score", 1)])["score"]
    score_parameters_cursor.update({"_id": 0}, {"$set": {"maximum_score": max_score}})
    score_parameters_cursor.update({"_id": 0}, {"$set": {"minimum_score": min_score}})

    # need to improve -> sum method
    total_score = float(0)
    for item in fluctlight_cursor.find({"deep_freeze": {"$ne": 1}}, {"score": 1}):
        total_score += item["score"]

    # save total score to week score log -> used in score weight update
    score_parameters_cursor.update_one({"_id": 0}, {"$push": {"week_score_log": total_score}})

    # update active logs
    # insert fluctlight_cursor, active_logs_cursor
    await active_logs_update(fluctlight_cursor, active_logs_cursor)

    # calculate test contribution, average test contribution
    # insert fluctlight_cursor
    # get avr_contrib
    avr_contrib = await contribution_update(fluctlight_cursor, active_logs_cursor)

    # calculate levelling index
    # insert score_parameters_cursor, fluctlight_cursor, active_logs_cursor
    await lvl_ind_update(fluctlight_cursor, active_logs_cursor, avr_contrib)

    # detect member levelling index reached warning range
    # insert self.bot, fluctlight_cursor
    await lvl_ind_detect(bot, fluctlight_cursor)

    # update score weight
    week_score_log = list(score_parameters_cursor.find_one({"_id": 0})["week_score_log"])
    avr_score_log = float(statistics.mean(week_score_log))

    new_weight = func.score_weight_update(total_score, avr_score_log, max_score, min_score)
    score_parameters_cursor.update_one({"_id": 0}, {"$set": {"score_weight": new_weight}})

    # old usage
    # add 1 to week_total_count
    # score_parameters_cursor.update_one({"_id": 0}, {"$inc": {"week_total_count": 1}})

    report_channel = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-report')
    await report_channel.send(f'[Auto]Very important update. {func.now_time_info("whole")}')


# vice functions

async def active_logs_update(fluctlight_cursor, active_logs_cursor):
    data = fluctlight_cursor.find({}, {"week_active": 1, "deep_freeze": 1})

    for member in data:
        member_id = member["_id"]
        member_active = str(member["week_active"])

        member_active_info = active_logs_cursor.find_one({"_id": member_id})

        if not member_active_info:
            if member["deep_freeze"] == 0:
                active_logs_cursor.insert({"_id": member_id, "log": member_active})
            elif member["deep_freeze"] == 1:
                active_logs_cursor.insert({"_id": member_id, "log": '1'})
        else:
            old_log = active_logs_cursor.find_one({"_id": member_id})["log"]

            if member["deep_freeze"] == 0:
                active_logs_cursor.update_one({"_id": member_id}, {"$set": {"log": str(member_active + old_log)}})
            elif member["deep_freeze"] == 1:
                active_logs_cursor.update_one({"_id": member_id}, {"$set": {"log": str(member_active + '1')}})

    fluctlight_cursor.update_many({}, {"$set": {"week_active": 0}})


async def contribution_update(fluctlight_cursor, active_logs_cursor):
    avr_contrib = float(0)
    data = active_logs_cursor.find({})

    for member in data:
        member_frozen = fluctlight_cursor.find_one({"_id": member["_id"]}, {"deep_freeze": 1})["deep_freeze"]

        if member_frozen == 1:
            continue

        total_contrib = float(0)
        for i, char in enumerate(member["log"]):
            total_contrib += pow(2, -i) * float(char)

        fluctlight_cursor.update_one({"_id": member["_id"]}, {"$inc": {"contrib": total_contrib}})
        avr_contrib += total_contrib

    total_member_count = len(list(fluctlight_cursor.find({"deep_freeze": {"$eq": 0}})))
    avr_contrib /= total_member_count

    return avr_contrib


async def lvl_ind_update(fluctlight_cursor, active_logs_cursor, avr_contrib):
    # old definition
    # total_week_count = score_parameters_cursor.find_one({"_id": 0})["week_total_count"]

    data = fluctlight_cursor.find({"deep_freeze": {"$eq": 0}}, {"contrib": 1})
    for member in data:
        member_active_logs = active_logs_cursor.find_one({"_id": member["_id"]})

        if not member_active_logs:
            continue

        # new definition
        member_week_count = len(member_active_logs["log"])

        active_logs = member_active_logs["log"]

        delta_lvl_ind = func.lvl_ind_calc(active_logs, member_week_count, member["contrib"], avr_contrib)
        fluctlight_cursor.update_one({"_id": member["_id"]}, {"$inc": {"lvl_ind": delta_lvl_ind}})


async def lvl_ind_detect(bot, fluctlight_cursor):
    data = fluctlight_cursor.find({}, {"contrib": 1, "lvl_ind": 1})

    sqcs_client = MongoClient(link)["sqcs-bot"]
    kick_member_cursor = sqcs_client["kick_member_list"]

    for member in data:
        if 1 <= member["lvl_ind"] < 1.5:
            user = await bot.guilds[0].fetch_member(member["_id"])
            await user.send(f'Your levelling index has reached warning range!({member["lvl_ind"]});')
        elif member["lvl_ind"] >= 1.5:
            user = await bot.guilds[0].fetch_member(member["_id"])
            await user.send(f'Your levelling index has reached danger range!({member["lvl_ind"]});')

            member_name = user.nick
            if member_name is None:
                member_name = user.name

            member_info = {
                "_id": user.id,
                "name": member_name,
                "contrib": member["contrib"],
                "lvl_ind": member["lvl_ind"]
            }
            kick_member_cursor.insert_one(member_info)
