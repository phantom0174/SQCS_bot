from core.classes import Cog_Extension
from discord.ext import commands
import functions as func
from core.setup import info, jdata
import discord
import json


class React(Cog_Extension):

    # bots communication event
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.author.bot == 'False' or ctx.author == self.bot.user or (
                ctx.channel != func.getChannel('_ToMV') or ctx.channel != func.getChannel('_ToSyn')):
            return

        MsgCont = str(ctx.content).split(' ')

        if MsgCont[0] == 'sw' and ctx.channel == func.getChannel('_ToMV'):
            with open('jsons/lecture.json', mode='r', encoding='utf8') as temp_file:
                lect_data = json.load(temp_file)

            lect_data['temp_sw'] = MsgCont[1]

            with open('jsons/lecture.json', mode='w', encoding='utf8') as temp_file:
                json.dump(lect_data, temp_file)

    @commands.command()
    async def msg_re(self, ctx, *, msg):
        re_msg = msg.split('\n')
        for msg in re_msg:
            await ctx.send(msg)

        await func.getChannel('_Report').send(f'[Command]msg_re used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(React(bot))
