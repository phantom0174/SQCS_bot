import discord
from .utils import Time
from .fluctlight_ext import Fluct
from .db.jsonstorage import JsonApi


async def report_lect_attend(bot, attendants: list, week: int) -> None:
    report_json = JsonApi.get('LectureLogging')
    guild = bot.get_guild(784607509629239316)
    report_channel = discord.utils.get(guild.text_channels, name='sqcs-lecture-attend')

    fluct_ext = Fluct(score_mode='lect_attend')
    for member_id in attendants:
        try:
            await fluct_ext.add_score(member_id)
            await fluct_ext.active_log_update(member_id)
            await fluct_ext.lect_attend_update(member_id)
        except BaseException:
            await report_channel.send(
                f'[DB MANI ERROR][to: {member_id}][score_mode: lect_attend]')

    report_json["logs"].append(
        f'[LECT ATTEND][week: {week}][attendants:\n'
        f'{attendants}\n'
        f'[{Time.get_info("whole")}]'
    )
    JsonApi.put('LectureLogging', report_json)
