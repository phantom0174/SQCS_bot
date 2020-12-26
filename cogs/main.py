from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client, link
import core.functions as func
import discord
from pymongo import MongoClient
import core.score_module as sm


class Main(Cog_Extension):
    # ping
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f':stopwatch: {round(self.bot.latency * 1000)} (ms)')

    # delete message
    @commands.command()
    async def clear(self, ctx, msg_id: int):
        find = bool(False)
        while not find:
            msg_logs = await ctx.channel.history(limit=50).flatten()
            for msg in msg_logs:
                await msg.delete()
                if msg.id == msg_id:
                    find = bool(True)
                    break

        await func.getChannel(self.bot, '_Report').send(f'[Command]clear used by user {ctx.author.id}. {func.now_time_info("whole")}')

    # member check
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def m_check(self, ctx):
        for member in ctx.guild.members:
            print(member)

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findid(self, ctx, search_name: str):
        for member in ctx.guild.members:
            if member.name == search_name:
                await ctx.send(f'{member.name} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def mibu(self, ctx, member_id: int):
        fluctlight_client = MongoClient(link)["LightCube"]
        fluctlight_cursor = fluctlight_client["light-cube-info"]

        fluctlight_cursor.update_one({"_id": member_id}, {"$inc": {"score": 5}})
        await sm.active_log_update(self.bot, member_id)

        await ctx.send('ok!')


def setup(bot):
    bot.add_cog(Main(bot))
