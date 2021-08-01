from datetime import datetime, timezone, timedelta
import math
import discord
from typing import Union


def sgn(num):
    if num > 0:
        return 1
    if num == 0:
        return 0

    return -1


class Time:
    @staticmethod
    def get_info(mode: str = 'custom', custom_form: str = '') -> Union[str, int, None]:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

        if mode == 'custom':
            return str(dt2.strftime(custom_form))

        if mode == 'whole':
            return str(dt2.strftime("%Y-%m-%d %H:%M:%S"))
        if mode == 'main':
            return str(dt2.strftime("%Y-%m-%d"))
        if mode == 'vice':
            return str(dt2.strftime("%H:%M:%S"))

        if mode == 'hour':
            return int(dt2.strftime("%H"))
        if mode == 'week_day':
            return int(dt2.isoweekday())
        if mode == 'day_of_week':
            return str(dt2.strftime("%A"))

        return None

    @staticmethod
    def get_range(hour) -> str:
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


class FluctMath:
    @staticmethod
    async def lvl_ind_calc(log, member_week_count, contrib, avr_contrib) -> float:
        theta1 = sgn(contrib - avr_contrib)

        active_days = sum(map(int, log))
        theta2 = sgn(active_days - (1 / 2) * member_week_count)

        return float(
            -sgn(theta1 + theta2) * abs((contrib - avr_contrib) * (theta1 + theta2)) / 2
        )

    @staticmethod
    def score_weight_update(t_score, avr_score, max_score, min_score) -> float:

        if max_score - min_score == 0:
            alpha = (t_score - avr_score)
        else:
            alpha = (t_score - avr_score) / (max_score - min_score)

        pt1 = float(1 / 2)
        pt2 = float(3 / (2 * (1 + pow(math.e, -5 * alpha + math.log(2)))))
        return pt1 + pt2


class DiscordExt:
    @staticmethod
    async def create_embed(title, thumbnail, color, fields_name, values) -> discord.Embed:
        if thumbnail == 'default':
            thumbnail = 'https://i.imgur.com/MbzRNTJ.png'

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
    async def get_member_nick_name(guild, member_id) -> str:
        member_name = guild.get_member(member_id).nick
        if member_name is None:
            member_name = guild.get_member(member_id).name

        return member_name


class ProgressDisplay:
    def __init__(self, channel: discord.TextChannel, content, total):
        self.channel = channel
        self.content = content
        self.total = total
        self.message = None

    async def active(self):
        message = await self.channel.send(f'{self.content} (0/{self.total})')
        self.message = message

    async def display(self, progress):
        if self.message is not None:
            await self.message.edit(content=f'{self.content} ({progress}/{self.total})')
