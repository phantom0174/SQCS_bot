from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import info, jdata
import functions as func
import discord


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

        await func.getChannel('_Report').send(f'[Command]clear used by user {ctx.author.id}. {func.now_time_info("whole")}')

    # member check
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def m_check(self, ctx):
        for member in ctx.guild.members:
            print(member)


def setup(bot):
    bot.add_cog(Main(bot))
