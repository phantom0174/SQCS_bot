from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import *
from functions import *
import discord


class Main(Cog_Extension):
    # ping
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{round(self.bot.latency * 1000)} (ms)')

    # delete message
    @commands.command()
    async def clear(self, ctx, msg):
        number = int(msg) + 1
        msg_logs = await ctx.channel.history(limit=number).flatten()
        for msg in msg_logs:
            await msg.delete()

        await getChannel('_Report').send(f'[Command]clear used by user {ctx.author.id}. {now_time_info("whole")}')

    # member check
    @commands.command()
    async def m_check(self, ctx):
        for member in ctx.guild.members:
            print(member)


def setup(bot):
    bot.add_cog(Main(bot))
