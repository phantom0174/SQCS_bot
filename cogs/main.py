from discord.ext import commands
from core.setup import client, rsp, fluctlight_client
import core.score_module as sm
from core.classes import CogExtension
import asyncio


class Main(CogExtension):
    # ping
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f':stopwatch: {round(self.bot.latency * 1000)} (ms)')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def common_role_give(self, ctx):
        common_role = ctx.guild.get_role(743654256565026817)
        for member in ctx.guild.members:
            if len(member.roles) == 1 and member.roles[0].name == '@everyone':
                await member.add_roles(common_role)

        await ctx.send(':white_check_mark: Operation finished!')

    # delete message
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def clear(self, ctx, msg_id: int):

        find = bool(False)
        while not find:
            msg_logs = await ctx.channel.history(limit=50).flatten()
            for msg in msg_logs:
                await msg.delete()
                if msg.id == msg_id:
                    find = bool(True)
                    break

    @commands.command()
    async def msg_repeat(self, ctx, *, msg):

        re_msg = msg.split('\n')
        for log in re_msg:
            await ctx.send(log)

    # member check
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def member_check(self, ctx):

        await ctx.send('The result can only be seen at the console!')
        for member in ctx.guild.members:
            print(member)

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvname(self, ctx, search_via_name: str):

        for member in ctx.guild.members:
            member_name = member.name

            if member_name.find(search_via_name) != -1:
                await ctx.send(f'{member_name} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvnick(self, ctx, search_via_nick: str):

        for member in ctx.guild.members:
            member_nick = member.nick
            if member_nick is None:
                continue

            if member_nick.find(search_via_nick) != -1:
                await ctx.send(f'{member_nick} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvid(self, ctx, search_via_id: int):

        for member in ctx.guild.members:
            if member.id != search_via_id:
                continue

            if member.name is None:
                return await ctx.send(f'{member.name} {member.id}')

            await ctx.send(f'{member.nick} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remedy(self, ctx, member_id: int, delta_value: float):
        fl_cursor = fluctlight_client["MainFluctlights"]
        score_set_cursor = client["ScoreSetting"]
        score_weight = score_set_cursor.find_one({"_id": 0})["score_weight"]

        try:
            execute = {
                "$inc": {
                    "score": round(delta_value * score_weight, 2)
                }
            }
            fl_cursor.update_one({"_id": member_id}, execute)
            await sm.active_log_update(member_id)

            member = ctx.guild.fetch_member(member_id)
            msg = f'耶！你被管理員加了 {delta_value} 分！' + '\n'
            msg += rsp["main"]["mibu"]["pt_1"]
            await member.send(msg)
        except:
            await ctx.send(f':exclamation: Error when remedying {member_id}, value: {delta_value}!')

        await ctx.send(':white_check_mark: Operation finished!')

    # active percentage
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def active_query(self, ctx):
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

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def rmvc(self, ctx, channel_id: int, countdown: int):  # remove member in voice channel
        countdown_duration = countdown
        voice_channel = self.bot.get_channel(channel_id)

        def content(s):
            return f':exclamation: 所有成員將在 {s} 秒後被移出 {voice_channel.name}'

        message = await ctx.send(content(countdown_duration))
        while countdown_duration > 0:
            await message.edit(content=content(countdown_duration))
            await asyncio.sleep(1)
            countdown_duration -= 1

        await message.delete()

        for member in voice_channel.members:
            await member.move_to(None)


def setup(bot):
    bot.add_cog(Main(bot))
