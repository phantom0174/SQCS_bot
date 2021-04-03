from core.classes import Cog_Extension
from discord.ext import commands
import core.functions as func
from core.setup import jdata, client, fluctlight_client
import discord
import json
import random


class Query(Cog_Extension):

    @commands.group()
    async def query(self, ctx):
        pass

    @query.command()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz(self, ctx):

        quiz_cursor = client["quiz_event"]
        data = quiz_cursor.find({})

        status = str()
        for item in data:
            member_name = (await self.bot.guilds[0].fetch_member(item["_id"])).nick
            if member_name is None:
                member_name = (await self.bot.fetch_member(item["_id"])).name

            status += f'{member_name}: {item["correct"]}\n'

        await ctx.send(status)
        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group query - quiz used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @query.command()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz_mani(self, ctx, member_id: int, alter: int):

        quiz_cursor = client["quiz"]
        quiz_cursor.update_one({"_id": member_id}, {"$set": {"correct": alter}})

        member_name = (await self.bot.fetch_user(member_id)).name
        await ctx.send(f'Member {member_name}\'s status has been set as {alter}')

        await func.getChannel(self.bot, '_Report').send(f'[Command]Group query - quiz_mani used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @query.command()
    async def all(self, ctx, msg):
        if msg == 'me' or func.role_check(ctx.author.roles, ['總召', 'Administrator']) is False:
            target_id = ctx.author.id
        else:
            target_id = int(msg)

        fluctlight_cursor = fluctlight_client["light-cube-info"]
        data = fluctlight_cursor.find_one({"_id": target_id})

        value_title = ['Object Id', 'Score', 'Durability', 'Object Control Authority', 'System Control Authority',
                       'Contribution', 'Levelling Index', "Deep Freeze"]
        obj_info = [data["_id"], data["score"], data["du"], data["oc_auth"], data["sc_auth"], data["contrib"],
                    data["lvl_ind"], data["deep_freeze"]]

        rand_icon = random.choice(jdata['fluctlight_gifs'])
        await ctx.author.send(embed=func.create_embed('Object info', rand_icon, 0xe46bf9, value_title, obj_info))

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group query - All used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Query(bot))
