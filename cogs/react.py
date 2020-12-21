from core.classes import Cog_Extension
from discord.ext import commands
import core.functions as func
import json


class React(Cog_Extension):

    @commands.command()
    async def msg_re(self, ctx, *, msg):
        re_msg = msg.split('\n')
        for log in re_msg:
            await ctx.send(log)

        await func.getChannel(self.bot, '_Report').send(f'[Command]msg_re used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(React(bot))
