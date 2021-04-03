from datetime import datetime, timezone, timedelta
from math import *
import discord
import json


<<<<<<< Updated upstream
=======
def sgn(num):
    if num > 0:
        return 1
    if num == 0:
        return 0

    return -1


>>>>>>> Stashed changes
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


def create_embed(Title, thumbnail, Color, FieldsName, Values):
    if thumbnail == 'default':
        thumbnail = 'https://i.imgur.com/26skltl.png'

    embed = discord.Embed(title=Title, color=Color)
    embed.set_thumbnail(url=thumbnail)
    if len(FieldsName) != len(Values):
        embed.add_field(name="Error", value='N/A', inline=False)
        return embed

    for (fn, vl) in zip(FieldsName, Values):
        embed.add_field(name=fn, value=vl, inline=False)

    embed.set_footer(text=now_time_info('whole'))
    return embed


def getChannel(bot, target):
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

<<<<<<< Updated upstream
    return 'morning'
=======
    return 'morning'


def DU_update(mdu, odu, time):
    if mdu != odu:
        d = time / 3600
        tau = -math.log(10 / abs(mdu - odu))
        return mdu + ((odu - mdu) * pow(math.e, -tau * d))

    return mdu


def lvl_ind_calc(log, member_week_count, contrib, avr_contrib):
    # calculate theta 1
    theta1 = sgn(contrib - avr_contrib)

    # calculate theta 2
    active_days = int(0)
    for char in log:
        active_days += int(char)
    theta2 = sgn(active_days - (1/2) * member_week_count)

    return float(-sgn(theta1 + theta2) * abs((contrib - avr_contrib) * (theta1 + theta2)) / 2)


def score_weight_update(t_score, avr_score, max_score, min_score):

    if max_score - min_score == 0:
        alpha = (t_score - avr_score)
    else:
        alpha = (t_score - avr_score) / (max_score - min_score)

    pt1 = float(1/2)
    pt2 = float(3/(2*(1 + pow(math.e, -5 * alpha + math.log(2)))))
    return pt1 + pt2
>>>>>>> Stashed changes
