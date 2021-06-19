from discord.ext import commands, tasks
from core.cog_config import CogExtension
import discord
from core.db import JsonApi
from core.utils import Time


class Log(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def log(self, ctx):
        pass

    @log.command(aliases=['query', 'len'])
    async def query_len(self, ctx, title: str = "CmdLogging"):
        title_options = ['CmdLogging', 'LectureLogging']
        if title not in title_options:
            return await ctx.send(
                f':x: 參數必須在 {title_options} 中！'
            )

        logs_list = JsonApi().get(title)["logs"]
        logs_length = len(logs_list)
        await ctx.send(f':mag_right: 記錄檔中目前有 {logs_length} 筆記錄！')

    @log.command(aliases=['get'])
    async def release(self, ctx, title: str = "CmdLogging"):
        logging_channel = {
            "CmdLogging": 785146879004508171,
            "LectureLogging": 828286118420021250
        }

        if title not in logging_channel.keys():
            return await ctx.send(f':x: 參數必須在 {logging_channel.keys()} 中！')

        buffer_channel = self.bot.get_channel(logging_channel.get(title))
        await release_log(title, buffer_channel, ctx.channel)


class CmdLogAuto(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.auto_release.start()

    @tasks.loop(hours=1)
    async def auto_release(self):
        logs_json = JsonApi().get('CmdLogging')

        if Time.get_info('hour') >= 18 and logs_json['daily_release'] is False:
            dev_guild = self.bot.get_guild(790978307235512360)
            auto_logging_channel = dev_guild.get_channel(855702933299658765)
            await release_log('CmdLogging', auto_logging_channel)

            logs_json['daily_release'] = True
            JsonApi().put('CmdLogging', logs_json)


async def release_log(title, target_channel: discord.TextChannel, report_channel: discord.TextChannel = None):
    logs_json = JsonApi().get(title)
    logs = '\n'.join(logs_json["logs"])

    with open('./txts/report_buffer.txt', mode='w', encoding='utf8') as temp_file:
        temp_file.write(logs)

    await target_channel.send(file=discord.File('./txts/report_buffer.txt'))

    if report_channel is not None:
        await report_channel.send(f':white_check_mark: 記錄檔 {title} 已釋出！')

    # clear buffer content
    with open('./txts/report_buffer.txt', mode='w', encoding='utf8') as temp_file:
        temp_file.write('')

    logs_json["logs"].clear()
    JsonApi().put(title, logs_json)


def setup(bot):
    bot.add_cog(Log(bot))
