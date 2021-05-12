from discord.ext import commands
from core.cog_config import CogExtension
import discord
from core.db import JsonApi


class Log(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def log(self, ctx):
        pass

    @log.command(aliases=['query', 'len'])
    async def query_len(self, ctx, title: str = "CmdLogging"):
        logs_list = JsonApi().get(title)["logs"]
        await ctx.send(f'There are currently {len(logs_list)} logs in the json file!')

    @log.command(aliases=['get'])
    async def release(self, ctx, title: str = "CmdLogging"):
        logging_channel = {
            "CmdLogging": "sqcs-report",
            "LectureLogging": "sqcs-lecture-report"
        }

        if title not in logging_channel.keys():
            return await ctx.send(f'There is no such logging named {title}!')

        buffer_channel = discord.utils.get(self.bot.guilds[1].text_channels, name=logging_channel[title])
        logs_json = JsonApi().get(title)

        if len(logs_json["logs"]) == 0:
            return

        logs = '\n'.join(logs_json["logs"])

        with open('./txts/report_buffer.txt', mode='w', encoding='utf8') as temp_file:
            temp_file.write(logs)

        # clear the string -> unnecessary
        # logs = ''

        await buffer_channel.send(file=discord.File('./txts/report_buffer.txt'))

        # clear buffer content
        with open('./txts/report_buffer.txt', mode='w', encoding='utf8') as temp_file:
            temp_file.write('')

        logs_json["logs"].clear()
        JsonApi().put(title, logs_json)


def setup(bot):
    bot.add_cog(Log(bot))
