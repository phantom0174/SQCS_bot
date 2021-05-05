from datetime import datetime, timezone, timedelta
import math
import discord
import core.score_module as sm
from core.cog_config import JsonApi
from core.db import self_client, fluctlight_client


def sgn(num):
    if num > 0:
        return 1
    if num == 0:
        return 0

    return -1


class Time:
    @staticmethod
    def get_info(mode):
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

        if mode == 'whole':
            return str(dt2.strftime("%Y-%m-%d %H:%M:%S"))
        if mode == 'hour':
            return int(dt2.strftime("%H"))
        if mode == 'date':
            return int(dt2.isoweekday())
        if mode == 'week':
            return str(dt2.strftime("%A"))

    @staticmethod
    def get_range(hour):
        morning = range(6, 12)
        noon = range(12, 13)
        after_noon = range(13, 18)
        evening = range(18, 24)
        night = range(0, 6)

        if hour in morning:
            return 'morning'
        if hour in noon:
            return 'noon'
        if hour in after_noon:
            return 'after_noon'
        if hour in evening:
            return 'evening'
        if hour in night:
            return 'night'

        return 'morning'


class FluctExt:
    @staticmethod
    async def report_lect_attend(bot, attendants, week):
        score_set_cursor = self_client["ScoreSetting"]
        score_weight = score_set_cursor.find_one({"_id": 0})["score_weight"]
        lect_attend_score = score_set_cursor.find_one({"_id": 0})["lecture_attend_point"]

        # add score to the attendances
        fluct_cursor = fluctlight_client["MainFluctlights"]

        report_json = JsonApi().get_json('LectureLogging')
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
                await sm.active_log_update(member_id)
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
        JsonApi().put_json('LectureLogging', report_json)

    @staticmethod
    def lvl_ind_calc(log, member_week_count, contrib, avr_contrib):
        theta1 = sgn(contrib - avr_contrib)

        active_days = sum(map(int, log))
        theta2 = sgn(active_days - (1 / 2) * member_week_count)

        return float(
            -sgn(theta1 + theta2) * abs((contrib - avr_contrib) * (theta1 + theta2)) / 2
        )

    @staticmethod
    def score_weight_update(t_score, avr_score, max_score, min_score):

        if max_score - min_score == 0:
            alpha = (t_score - avr_score)
        else:
            alpha = (t_score - avr_score) / (max_score - min_score)

        pt1 = float(1 / 2)
        pt2 = float(3 / (2 * (1 + pow(math.e, -5 * alpha + math.log(2)))))
        return pt1 + pt2


class DiscordExt:
    @staticmethod
    def create_embed(title, thumbnail, color, fields_name, values):
        if thumbnail == 'default':
            thumbnail = 'https://i.imgur.com/26skltl.png'

        embed = discord.Embed(title=title, color=color)
        embed.set_thumbnail(url=thumbnail)
        if len(fields_name) != len(values):
            embed.add_field(name="Error", value='N/A', inline=False)
            return embed

        for (fn, vl) in zip(fields_name, values):
            embed.add_field(name=fn, value=vl, inline=False)

        embed.set_footer(text=Time.get_info('whole'))
        return embed

    @staticmethod
    async def get_member_nick_name(guild, member_id):
        member_name = (await guild.fetch_member(member_id)).nick
        if member_name is None:
            member_name = (await guild.fetch_member(member_id)).name

        return member_name
