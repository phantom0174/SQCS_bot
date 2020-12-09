from datetime import datetime, timezone, timedelta
from math import *
import discord
import json

global _ToSyn
global _ToMV
global _Report


def now_time_info(mode):
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

    if mode == 'whole':
        return str(dt2.strftime("%Y-%m-%d %H:%M:%S"))
    elif mode == 'hour':
        return int(dt2.strftime("%H"))
    elif mode == 'date':
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

    for i in range(len(FieldsName)):
        embed.add_field(name=FieldsName[i], value=Values[i], inline=False)

    embed.set_footer(text=now_time_info('whole'))
    return embed


def setChannel(bot):
    global _ToSyn
    global _ToMV
    global _Report

    _ToSyn = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-and-syn')
    _ToMV = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-and-mv')
    _Report = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-report')


def getChannel(target):
    global _ToSyn
    global _ToMV
    global _Report

    if target == '_ToSyn':
        return _ToSyn
    elif target == '_ToMV':
        return _ToMV
    elif target == '_Report':
        return _Report
