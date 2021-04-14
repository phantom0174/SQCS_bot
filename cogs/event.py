from core.classes import Cog_Extension, JsonApi
from discord.ext import commands
import discord
import core.functions as func


class Event(Cog_Extension):

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(content=f'`{error}`', delete_after=5.0)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        cmd_name = ctx.command.name
        cmd_parents = ctx.command.full_parent_name
        channel_name = ctx.channel.name
        user_name = ctx.author.name
        user_id = ctx.author.id
        message = ctx.message.content

        if len(cmd_parents) == 0:
            cmd_parents = str('N/A')

        log_msg = f'[{cmd_parents}][{cmd_name}], [{channel_name}], [{user_name}][{user_id}]\n[{message}]\n'
        full_log = f'[cmd exec]{log_msg}[{func.now_time_info("whole")}]'

        log_json = JsonApi().get_json('CmdLogging')
        log_json['logs'].append(full_log)
        JsonApi().put_json('CmdLogging', log_json)

    @commands.group()
    async def log(self, ctx):
        pass

    @log.command()
    async def query_len(self, ctx, title: str = "CmdLogging"):
        logs_list = JsonApi().get_json(title)["logs"]
        await ctx.send(f'There are currently {len(logs_list)} logs in the json file!')

    @log.command()
    async def release(self, ctx, title: str = "CmdLogging"):
        logging_channel = {
            "CmdLogging": "sqcs-report",
            "LectureLogging": "sqcs-lecture-report"
        }

        if title not in logging_channel.keys():
            await ctx.send(f'There is no such logging named {title}!')
            return

        buffer_channel = discord.utils.get(self.bot.guilds[1].text_channels, name=logging_channel[title])
        logs_json = JsonApi().get_json(title)

        if len(logs_json["logs"]) == 0:
            return

        logs = str()
        for item in logs_json["logs"]:
            logs += f'{item}\n'

        with open('./txts/report_buffer.txt', mode='w', encoding='utf8') as temp_file:
            temp_file.write(logs)

        # clear the string
        logs = ''

        await buffer_channel.send(file=discord.File('./txts/report_buffer.txt'))

        # clear buffer content
        with open('./txts/report_buffer.txt', mode='w', encoding='utf8') as temp_file:
            temp_file.write('')

        logs_json["logs"].clear()
        JsonApi().put_json(title, logs_json)


def setup(bot):
    bot.add_cog(Event(bot))
