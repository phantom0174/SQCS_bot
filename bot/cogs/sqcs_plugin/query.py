from discord.ext import commands
import random
from ...core.utils import DiscordExt
from ...core.db.jsonstorage import JsonApi
from ...core.db.mongodb import Mongo
from ...core.cog_config import CogExtension
import discord


class Query(CogExtension):

    @commands.group()
    async def query(self, ctx):
        pass

    @query.command()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz(self, ctx):
        """cmd
        查詢懸賞活動的目前狀態。
        """
        quiz_ongoing_cursor = Mongo('sqcs-bot').get_cur('QuizOngoing')
        data = quiz_ongoing_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':x: 沒有任何正在進行中的懸賞活動！')

        status = ''
        for item in data:
            member_name = await DiscordExt.get_member_nick_name(ctx.guild, item["_id"])
            status += f'{member_name}: {item["correct"]}\n'

            if len(status) > 1600:
                await ctx.send(status)

        if len(status) > 0:
            await ctx.send(status)

    @query.command()
    async def my_data(self, ctx):
        """cmd
        查詢個人搖光資料。
        """
        try:
            await ctx.author.send(embed=(await create_fluct_data_embed(ctx.author.id)))
        except BaseException:
            pass

    @query.command()
    @commands.has_any_role('總召', 'Administrator')
    async def member_data(self, ctx, target_id: int):
        """cmd
        查詢 成員<target_id> 的搖光資料。

        .target_id: 成員的Discord id
        """
        try:
            await ctx.author.send(embed=(await create_fluct_data_embed(target_id)))
        except BaseException:
            pass

    # guild active percentage
    @query.command()
    async def guild_active(self, ctx):
        """cmd
        查詢伺服器活躍度。
        """
        fluct_cursor = Mongo('LightCube').get_cur('MainFluctlights')
        week_active_match = {
            "deep_freeze": {
                "$ne": True
            },
            "week_active": {
                "$ne": False
            }
        }
        week_active_count = fluct_cursor.find(week_active_match).count()
        countable_member_count = fluct_cursor.find({"deep_freeze": {"$ne": 1}}).count()
        activeness = round((week_active_count / countable_member_count) * 100, 4)

        await ctx.send(
            f':scroll: 伺服器目前活躍度為 {activeness}%\n'
            f'總人數：{countable_member_count}\n'
            f'活躍中：{week_active_count}'
        )


async def create_fluct_data_embed(member_id) -> discord.Embed:
    fluct_cursor = Mongo('LightCube').get_cur('MainFluctlights')
    data = fluct_cursor.find_one({"_id": member_id})

    # method used when checking a dict is empty or not
    if not data:
        embed_para = [
            'Object info',
            'default',
            0xe46bf9,
            ['Error'],
            ['Logging error']
        ]
        return await DiscordExt.create_embed(*embed_para)

    value_title = [
        'Member id',
        'Name',
        'Score',
        'Weekly activeness',
        'Contribution',
        'Levelling index',
        'Deep Freeze'
    ]
    obj_info = [
        data["_id"],
        data["name"],
        data["score"],
        data["week_active"],
        data["contrib"],
        data["lvl_ind"],
        data["deep_freeze"]
    ]

    icon_json = JsonApi.get('StaticSetting')
    rand_icon = random.choice(icon_json['fluctlight_query_gifs'])

    embed_para = [
        'Object info',
        rand_icon,
        0xe46bf9,
        value_title,
        obj_info
    ]
    return await DiscordExt.create_embed(*embed_para)


def setup(bot):
    bot.add_cog(Query(bot))
