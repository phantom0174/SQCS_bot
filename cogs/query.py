from core.classes import Cog_Extension
from discord.ext import commands
import functions as func
from core.setup import jdata, client
import discord
import json


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
            if member_name == None:
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


def setup(bot):
    bot.add_cog(Query(bot))
