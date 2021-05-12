from core.db import self_client, fluctlight_client, JsonApi
import discord
from core.utils import Time
import core.fluctlight_ext as fluct_ext


async def report_lect_attend(bot, attendants: list, week: int) -> None:
    score_set_cursor = self_client["ScoreSetting"]
    score_weight = score_set_cursor.find_one({"_id": 0})["score_weight"]
    lect_attend_score = score_set_cursor.find_one({"_id": 0})["lecture_attend_point"]

    # add score to the attendances
    fluct_cursor = fluctlight_client["MainFluctlights"]

    report_json = JsonApi().get('LectureLogging')
    report_channel = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-lecture-attend')

    for member_id in attendants:
        delta_score = round(lect_attend_score * score_weight, 2)
        try:
            execute = {
                "$inc": {
                    "score": delta_score
                }
            }
            fluct_cursor.update_one({"_id": member_id}, execute)
            fluct_ext.Fluct().active_log_update(member_id)
            fluct_ext.Fluct().lect_attend_update(member_id)
        except:
            await report_channel.send(
                f'[DB MANI ERROR][to: {member_id}]'
                f'[inc_score: {delta_score}]'
            )

    report_json["logs"].append(
        f'[LECT ATTEND][week: {week}][attendants:\n'
        f'{attendants}\n'
        f'[{Time.get_info("whole")}]'
    )
    JsonApi().put('LectureLogging', report_json)
