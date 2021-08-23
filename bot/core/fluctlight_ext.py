import statistics
import discord
from .db.mongodb import Mongo
from .utils import Time, FluctMath, DiscordExt
from typing import NoReturn


class Fluct:
    def __init__(self, member_id=None, score_mode=None):
        cursors_collection = ['MainFluctlights', 'ViceFluctlights']
        self.main_fluct_cursor, self.vice_fluct_cursor = Mongo('LightCube').get_curs(cursors_collection)

        # score setting cursor
        self.delta_score = None
        if score_mode is not None:
            self.score_mode = score_mode

            score_set_cursor = Mongo('sqcs-bot').get_cur('ScoreSetting')
            score_setting = score_set_cursor.find_one({"_id": 0})
            self.score_weight = score_setting["score_weight"]

            if score_mode != 'custom':
                score_modes = {
                    "lect_attend": "lecture_attend_point",
                    "quiz": "quiz_point"
                }
                if score_mode not in score_modes.keys():
                    raise BaseException('ARGUMENT ERROR: score_mode', score_mode)

                self.delta_score = score_setting[score_modes.get(score_mode)]

        self.member_id = None
        if member_id is not None:
            self.member_id = member_id

    async def get_final_id(self, input_member_id):
        if self.member_id is not None:
            return self.member_id
        return input_member_id

    async def create_main(self, guild, deep_freeze_status: bool, member_id: int = -1) -> None:
        member_final_id = await self.get_final_id(member_id)

        default_main_fluctlight = {
            "_id": member_final_id,
            "name": await DiscordExt.get_member_nick_name(guild, member_final_id),
            "score": 0,
            "week_active": False,
            "contrib": 0,
            "lvl_ind": 0,
            "deep_freeze": deep_freeze_status,
            "log": '',
            "lect_attend_count": 0,
            "quiz_submit_count": 0,
            "quiz_correct_count": 0
        }
        try:
            self.main_fluct_cursor.insert_one(default_main_fluctlight)
        except BaseException:
            pass

    async def delete_main(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        try:
            self.main_fluct_cursor.delete_one({"_id": member_final_id})
        except BaseException:
            pass

    async def reset_main(self, guild, deep_freeze_status: bool, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        await self.delete_main(member_final_id)
        await self.create_main(guild, deep_freeze_status, member_final_id)

    async def create_vice(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        default_vice_fluctlight = {
            "_id": member_final_id,
            "du": 0,
            "mdu": 0,
            "oc_auth": 0,
            "sc_auth": 0,
        }
        try:
            self.vice_fluct_cursor.insert_one(default_vice_fluctlight)
        except BaseException:
            pass

    async def delete_vice(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        try:
            self.vice_fluct_cursor.delete_one({"_id": member_final_id})
        except BaseException:
            pass

    async def reset_vice(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        await self.delete_vice(member_final_id)
        await self.create_vice(member_final_id)

    async def add_score(self, member_id: int = -1, delta_value: float = -1) -> float:
        member_final_id = await self.get_final_id(member_id)
        if self.score_mode == 'custom':
            final_delta_score = delta_value
        else:
            final_delta_score = self.delta_score

        final_delta_score = round(self.score_weight * final_delta_score, 2)

        execute = {
            "$inc": {
                "score": final_delta_score
            }
        }
        self.main_fluct_cursor.update_one({"_id": member_final_id}, execute)
        return final_delta_score

    async def active_log_update(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        execute = {
            "$set": {
                "week_active": True
            }
        }
        self.main_fluct_cursor.update_one({"_id": member_final_id}, execute)

    async def lect_attend_update(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        execute = {
            "$inc": {
                "lect_attend_count": 1
            }
        }
        self.main_fluct_cursor.update_one({"_id": member_final_id}, execute)

    async def quiz_submit_update(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        execute = {
            "$inc": {
                "quiz_submit_count": 1
            }
        }
        self.main_fluct_cursor.update_one({"_id": member_final_id}, execute)

    async def quiz_correct_update(self, member_id: int = -1) -> NoReturn:
        member_final_id = await self.get_final_id(member_id)
        execute = {
            "$inc": {
                "quiz_correct_count": 1
            }
        }
        self.main_fluct_cursor.update_one({"_id": member_final_id}, execute)


# main function
async def guild_weekly_update(bot) -> NoReturn:

    # ------------------------------
    # Very important update function
    # ------------------------------

    # set-up self_client
    fluctlight_cursor = Mongo('LightCube').get_cur('MainFluctlights')
    score_set_cursor = Mongo('sqcs-bot').get_cur('ScoreSetting')

    # calculate total score, max, min score
    max_score = fluctlight_cursor.find({}, {"score": 1}).sort("score", -1)[0]["score"]
    min_score = fluctlight_cursor.find({}, {"score": 1}).sort("score", 1)[0]["score"]
    score_set_cursor.update({"_id": 0}, {"$set": {"maximum_score": max_score}})
    score_set_cursor.update({"_id": 0}, {"$set": {"minimum_score": min_score}})

    # improved sum method
    without_frozen_member_cursor = fluctlight_cursor.find({"deep_freeze": {"$ne": True}})
    total_score = sum(map(lambda item: item["score"], without_frozen_member_cursor))

    # save total score to week score log -> used in score weight update
    score_set_cursor.update_one({"_id": 0}, {"$push": {"week_score_log": total_score}})

    # update active logs
    # insert fluctlight_cursor, active_logs_cursor
    await active_logs_update(fluctlight_cursor)

    # calculate test contribution, average test contribution
    # insert fluctlight_cursor
    # get avr_contrib
    avr_contrib = await contribution_update(fluctlight_cursor)

    # calculate levelling index
    # insert score_set_cursor, fluctlight_cursor, active_logs_cursor
    await lvl_ind_update(fluctlight_cursor, avr_contrib)

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
async def active_logs_update(fluctlight_cursor) -> None:
    data = fluctlight_cursor.find({})

    for member in data:
        member_active = '1' if member["week_active"] else '0'

        old_log = fluctlight_cursor.find_one({"_id": member["_id"]})["log"]
        if not member["deep_freeze"]:
            execute = {
                "$set": {
                    "log": member_active + old_log
                }
            }
            fluctlight_cursor.update_one({"_id": member["_id"]}, execute)
        elif member["deep_freeze"]:
            execute = {
                "$set": {
                    "log": '1' + old_log
                }
            }
            fluctlight_cursor.update_one({"_id": member["_id"]}, execute)

    fluctlight_cursor.update_many({}, {"$set": {"week_active": False}})


async def contribution_update(fluctlight_cursor) -> float:
    avr_contrib = float(0)
    data = fluctlight_cursor.find({})

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


async def lvl_ind_update(fluctlight_cursor, avr_contrib) -> None:
    data = fluctlight_cursor.find({"deep_freeze": {"$eq": False}})
    for member in data:
        member_active_logs = fluctlight_cursor.find_one({"_id": member["_id"]})

        member_week_count = len(member_active_logs["log"])
        active_logs = member_active_logs["log"]
        delta_lvl_ind = await FluctMath.lvl_ind_calc(
            active_logs,
            member_week_count,
            member["contrib"],
            avr_contrib
        )
        fluctlight_cursor.update_one({"_id": member["_id"]}, {"$inc": {"lvl_ind": delta_lvl_ind}})


async def lvl_ind_detect(bot, fluctlight_cursor) -> None:
    kick_cursor = Mongo('sqcs-bot').get_cur('ReadyToKick')
    guild = bot.get_guild(743507979369709639)

    data = fluctlight_cursor.find({})
    for member in data:
        if 1 <= member["lvl_ind"] < 1.5:
            user = guild.get_member(member["_id"])
            try:
                await user.send(f'Your levelling index has reached warning range!({member["lvl_ind"]});')
            except BaseException:
                pass
        elif member["lvl_ind"] >= 1.5:
            user = guild.get_member(member["_id"])
            try:
                await user.send(f'Your levelling index has reached danger range!({member["lvl_ind"]});')
            except BaseException:
                pass

            member_info = {
                "_id": user.id,
                "name": user.display_name,
                "contrib": member["contrib"],
                "lvl_ind": member["lvl_ind"]
            }
            kick_cursor.insert_one(member_info)
