from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client, link, rsp, fluctlight_client
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

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]clear used by user {ctx.author.id}. {func.now_time_info("whole")}')

    # member check
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def member_check(self, ctx):
        await ctx.send('The result can only be seen at the console!')
        for member in ctx.guild.members:
            print(member)

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvname(self, ctx, search_name):
        for member in ctx.guild.members:
            member_name = member.name

            if member_name.find(search_name) != -1:
                await ctx.send(f'{member_name} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvnick(self, ctx, search_name):
        for member in ctx.guild.members:
            member_nick = member.nick
            if member_nick is None:
                continue

            if member_nick.find(search_name) != -1:
                await ctx.send(f'{member_nick} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvid(self, ctx, search_id: int):
        for member in ctx.guild.members:
            if member.id != search_id:
                continue

            if member.name is None:
                await ctx.send(f'{member.name} {member.id}')
                return

            await ctx.send(f'{member.nick} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def mibu(self, ctx, member_id: int, delta_value: str):
        fluctlight_cursor = fluctlight_client["light-cube-info"]
        score_parameters_cursor = client["score_parameters"]

        score_weight = score_parameters_cursor.find_one({"_id": 0})["score_weight"]

        try:
            fluctlight_cursor.update_one({"_id": member_id}, {"$inc": {"score": float(delta_value) * score_weight}})
            await sm.active_log_update(member_id)

            member = ctx.guild.fetch_member(member_id)
            msg = f'耶！你被管理員加了 {delta_value} 分！' + '\n'
            msg += rsp["main"]["mibu"]["pt_1"]
            await member.send(msg)
        except:
            await ctx.send(':exclamation: Error when manipulating!')

        await ctx.send('ok!')

    # active percentage
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def active_query(self, ctx):
        fluctlight_cursor = fluctlight_client["light-cube-info"]
        active_data = list(fluctlight_cursor.find({"deep_freeze": {"$ne": 1}, "week_active": {"$ne": 0}}))
        true_data = list(fluctlight_cursor.find({"deep_freeze": {"$ne": 1}}))

        active = len(active_data)
        true = len(true_data)

        await ctx.send(f':scroll: Weekly activeness until now is {(active / true) * 100} %\n'
                       f'Active: {active}, Total: {true}')


def setup(bot):
    bot.add_cog(Main(bot))
