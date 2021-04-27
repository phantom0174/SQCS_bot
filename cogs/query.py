from discord.ext import commands
import random
import core.functions as func
from core.setup import client, fluctlight_client
from core.classes import CogExtension, JsonApi


class Query(CogExtension):

    @commands.group()
    async def query(self, ctx):
        pass

    @query.command()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz(self, ctx):

        quiz_ongoing_cursor = client["QuizOngoing"]
        data = quiz_ongoing_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':exclamation: There is no data!')

        status = str()
        for item in data:
            member_name = await func.get_member_nick_name(ctx.guild, item["_id"])
            status += f'{member_name}: {item["correct"]}\n'

            if len(status) > 1600:
                await ctx.send(status)

        if len(status) > 0:
            await ctx.send(status)

    @query.command()
    async def my_data(self, ctx):
        await ctx.author.send(embed=(await personal_info(ctx.author.id)))

    @query.command()
    @commands.has_any_role('總召', 'Administrator')
    async def member_data(self, ctx, target_id: int):
        await ctx.author.send(embed=(await personal_info(target_id)))

    # guild active percentage
    @query.command()
    async def guild_active(self, ctx):
        fluct_cursor = fluctlight_client["MainFluctlights"]
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

        await ctx.send(
            f':scroll: Weekly activeness until now is {(week_active_count / countable_member_count) * 100} %\n'
            f'Active: {week_active_count}, Total: {countable_member_count}'
        )


async def personal_info(member_id):
    fluct_cursor = fluctlight_client["MainFluctlights"]
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
        return func.create_embed(*embed_para)

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

    icon_json = JsonApi().get_json('StaticSetting')
    rand_icon = random.choice(icon_json['fluctlight_query_gifs'])

    embed_para = [
        'Object info',
        rand_icon,
        0xe46bf9,
        value_title,
        obj_info
    ]
    return func.create_embed(*embed_para)


def setup(bot):
    bot.add_cog(Query(bot))
