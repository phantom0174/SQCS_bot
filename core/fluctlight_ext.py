import statistics
import discord
from core.db import self_client, fluctlight_client
from core.utils import Time, FluctMath, DiscordExt


class Fluct:
    def __init__(self, member_id=None):
        self.main_fluct_cursor = fluctlight_client["MainFluctlights"]
        self.vice_fluct_cursor = fluctlight_client["ViceFluctlights"]
        self.act_cursor = fluctlight_client["ActiveLogs"]

        if member_id is not None:
            self.member_fluctlight = self.main_fluct_cursor.find_one({"_id": member_id})

    async def reset_main(self, member_id, guild) -> None:
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

    def reset_vice(self, member_id) -> None:
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

    def reset_active(self, member_id) -> None:
        default_act = {
            "_id": member_id,
            "log": '',
            "lect_attend_count": 0,
            "quiz_submit_count": 0,
            "quiz_correct_count": 0
        }
        try:
            self.act_cursor.delete_one({"_id": member_id})
        except:
            pass

        try:
            self.act_cursor.insert_one(default_act)
        except:
            pass

    def active_log_update(self, member_id: int) -> None:
        active = self.main_fluct_cursor.find_one({"_id": member_id})["week_active"]
        if not active:
            execute = {
                "$set": {
                    "week_active": True
                }
            }
            self.main_fluct_cursor.update_one({"_id": member_id}, execute)

    def lect_attend_update(self, member_id: int) -> None:
        data = self.act_cursor.find_one({"_id": member_id})
        if not data:
            self.reset_active(member_id)

        execute = {
            "$inc": {
                "lect_attend_count": 1
            }
        }
        self.act_cursor.update_one({"_id": member_id}, execute)

    def quiz_submit_update(self, member_id: int) -> None:
        data = self.act_cursor.find_one({"_id": member_id})
        if not data:
            self.reset_active(member_id)

        execute = {
            "$inc": {
                "quiz_submit_count": 1
            }
        }
        self.act_cursor.update_one({"_id": member_id}, execute)

    def quiz_correct_update(self, member_id: int) -> None:
        data = self.act_cursor.find_one({"_id": member_id})
        if not data:
            self.reset_active(member_id)

        execute = {
            "$inc": {
                "quiz_correct_count": 1
            }
        }
        self.act_cursor.update_one({"_id": member_id}, execute)


# main function
async def guild_weekly_update(bot) -> None:

    # ------------------------------
    # Very important update function
    # ------------------------------

    # set-up self_client
    fluctlight_cursor = fluctlight_client["MainFluctlights"]
    score_set_cursor = self_client["ScoreSetting"]
    active_logs_cursor = fluctlight_client["ActiveLogs"]

    # calculate total score, max, min score
    max_score = fluctlight_cursor.find_one({}, {"score": 1}, sort=[("score", -1)])["score"]
    min_score = fluctlight_cursor.find_one({}, {"score": 1}, sort=[("score", 1)])["score"]
    score_set_cursor.update({"_id": 0}, {"$set": {"maximum_score": max_score}})
    score_set_cursor.update({"_id": 0}, {"$set": {"minimum_score": min_score}})

    # improved sum method
    without_frozen_member_cursor = fluctlight_cursor.find({"deep_freeze": {"$ne": True}})
    total_score = sum(map(lambda item: item["score"], without_frozen_member_cursor))

    # save total score to week score log -> used in score weight update
    score_set_cursor.update_one({"_id": 0}, {"$push": {"week_score_log": total_score}})

    # update active logs
    # insert fluctlight_cursor, active_logs_cursor
    await active_logs_update(fluctlight_cursor, active_logs_cursor)

    # calculate test contribution, average test contribution
    # insert fluctlight_cursor
    # get avr_contrib
    avr_contrib = await contribution_update(fluctlight_cursor, active_logs_cursor)

    # calculate levelling index
    # insert score_set_cursor, fluctlight_cursor, active_logs_cursor
    await lvl_ind_update(fluctlight_cursor, active_logs_cursor, avr_contrib)

    # detect member levelling index reached warning range
    # insert self.bot, fluctlight_cursor
    await lvl_ind_detect(bot, fluctlight_cursor)

    # update score weight
    week_score_log = list(score_set_cursor.find_one({"_id": 0})["week_score_log"])
    avr_score_log = float(statistics.mean(week_score_log))

    new_weight = FluctMath.score_weight_update(total_score, avr_score_log, max_score, min_score)
    score_set_cursor.update_one({"_id": 0}, {"$set": {"score_weight": new_weight}})

    report_channel = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-report')
    await report_channel.send(f'[Auto]Very important update. {Time.get_info("whole")}')


# vice functions
async def active_logs_update(fluctlight_cursor, active_logs_cursor) -> None:
    data = fluctlight_cursor.find({})

    for member in data:
        member_id = member["_id"]
        member_active = '1' if member["week_active"] else '0'

        member_active_info = active_logs_cursor.find_one({"_id": member_id})

        if not member_active_info:
            if not member["deep_freeze"]:
                active_logs_cursor.insert({"_id": member_id, "log": member_active})
            elif member["deep_freeze"]:
                active_logs_cursor.insert({"_id": member_id, "log": '1'})
        else:
            old_log = active_logs_cursor.find_one({"_id": member_id})["log"]

            if not member["deep_freeze"]:
                execute = {
                    "$set": {
                        "log": member_active + old_log
                    }
                }
                active_logs_cursor.update_one({"_id": member_id}, execute)
            elif member["deep_freeze"]:
                execute = {
                    "$set": {
                        "log": '1' + old_log
                    }
                }
                active_logs_cursor.update_one({"_id": member_id}, execute)

    fluctlight_cursor.update_many({}, {"$set": {"week_active": False}})


async def contribution_update(fluctlight_cursor, active_logs_cursor) -> float:
    avr_contrib = float(0)
    data = active_logs_cursor.find({})

    for member in data:
        member_frozen = fluctlight_cursor.find_one({"_id": member["_id"]})["deep_freeze"]

        if member_frozen:
            continue

        total_contrib = float(0)
        for i, char in enumerate(member["log"]):
            total_contrib += pow(2, -i) * float(char)

        fluctlight_cursor.update_one({"_id": member["_id"]}, {"$inc": {"contrib": total_contrib}})
        avr_contrib += total_contrib

    total_member_count = fluctlight_cursor.find({"deep_freeze": {"$eq": False}}).count()
    avr_contrib /= total_member_count

    return avr_contrib


async def lvl_ind_update(fluctlight_cursor, active_logs_cursor, avr_contrib) -> None:
    data = fluctlight_cursor.find({"deep_freeze": {"$eq": False}})
    for member in data:
        member_active_logs = active_logs_cursor.find_one({"_id": member["_id"]})

        if not member_active_logs:
            Fluct().reset_active(member["_id"])

        member_week_count = len(member_active_logs["log"])
        active_logs = member_active_logs["log"]
        delta_lvl_ind = FluctMath.lvl_ind_calc(
            active_logs,
            member_week_count,
            member["contrib"],
            avr_contrib
        )

        fluctlight_cursor.update_one({"_id": member["_id"]}, {"$inc": {"lvl_ind": delta_lvl_ind}})


async def lvl_ind_detect(bot, fluctlight_cursor) -> None:
    kick_cursor = self_client["ReadyToKick"]

    data = fluctlight_cursor.find({})
    for member in data:
        if 1 <= member["lvl_ind"] < 1.5:
            user = await bot.guilds[0].fetch_member(member["_id"])
            await user.send(f'Your levelling index has reached warning range!({member["lvl_ind"]});')
        elif member["lvl_ind"] >= 1.5:
            user = await bot.guilds[0].fetch_member(member["_id"])
            await user.send(f'Your levelling index has reached danger range!({member["lvl_ind"]});')

            member_info = {
                "_id": user.id,
                "name": user.display_name,
                "contrib": member["contrib"],
                "lvl_ind": member["lvl_ind"]
            }
            kick_cursor.insert_one(member_info)

"""
async def hurt(member_id, delta_du):
    fluct_cursor = fluctlight_client["light-cube-info"]
    member_fluctlight = fluct_cursor.find_one({"_id": member_id})
    current_du = member_fluctlight["du"]

    if current_du <= delta_du:
        return 'dead'
    else:
        execute = {
            "$inc": {
                "du": -delta_du
            }
        }
        fluct_cursor.update_one({"_id": member_id}, execute)

        regeneration_json = JsonApi().get('FluctlightEvent')
        if member_id not in regeneration_json["regen_id_list"]:
            regeneration_json["id_list"].append(member_id)
            JsonApi().put('FluctlightEvent', regeneration_json)

            regeneration_task = threading.Thread(target=regeneration, args=(member_id,))
            regeneration_task.start()

        return 'alive'


# def respawn_cool_down(member_id):


def regeneration(member_id):
    fluct_cursor = fluctlight_client["light-cube-info"]

    while True:
        member_fluctlight = fluct_cursor.find_one({"_id": member_id})
        current_du = member_fluctlight["du"]
        mdu = member_fluctlight["mdu"]

        regenerate_du = math.floor(mdu / 100)
        if current_du + regenerate_du < mdu:
            execute = {
                "$inc": {
                    "du": regenerate_du
                }
            }
            fluct_cursor.update_one({"_id": member_id}, execute)
        else:
            execute = {
                "$set": {
                    "du": mdu
                }
            }
            fluct_cursor.update_one({"_id": member_id}, execute)
            break

        # wait 1 tic
        time.sleep(10)
"""