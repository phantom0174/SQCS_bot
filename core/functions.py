from datetime import datetime, timezone, timedelta
from math import *
import discord
import json


def now_time_info(mode):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

    if mode == 'whole':
        return str(dt2.strftime("%Y-%m-%d %H:%M:%S"))
    if mode == 'hour':
        return int(dt2.strftime("%H"))
    if mode == 'date':
        return int(dt2.isoweekday())


def role_check(roles, target_roles):
    for role in roles:
        if role.name in target_roles:
            return True

    return False


def create_embed(Title, Color, FieldsName, Values):
    embed = discord.Embed(title=Title, color=Color)
    embed.set_thumbnail(url="https://i.imgur.com/26skltl.png")
    if len(FieldsName) != len(Values):
        embed.add_field(name="Error", value='N/A', inline=False)
        return embed

    for (fn, vl) in zip(FieldsName, Values):
        embed.add_field(name=fn, value=vl, inline=False)

    embed.set_footer(text=now_time_info('whole'))
    return embed


def getChannel(bot, target):
    if target == '_ToSyn':
        return discord.utils.get(bot.guilds[1].text_channels, name='sqcs-and-syn')
    if target == '_ToMV':
        return discord.utils.get(bot.guilds[1].text_channels, name='sqcs-and-mv')
    if target == '_Report':
        return discord.utils.get(bot.guilds[1].text_channels, name='sqcs-report')


async def get_time_title(hour):
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