import discord
from discord.ext import commands
from ..core.utils import Time
from ..core.cog_config import CogExtension
from ..core.db.jsonstorage import JsonApi
import traceback


class ErrorHandler(CogExtension):
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        log_channel = self.bot.get_channel(785146879004508171)
        await ctx.send(content=f'`{error}`', delete_after=8.0)

        # search for real traceback breakpoint
        error_message = traceback.format_exception(type(error), error, error.__traceback__)
        until_index = None

        for index, msg in enumerate(error_message):
            if msg.find('The above exception') != -1:
                until_index = int(index)
                break
        if until_index is None:
            until_index = len(error_message) - 1

        msg = '\n'.join(error_message[:until_index])
        await log_channel.send(
            f'[{Time.get_info("whole")}][CMD ERROR][{error}]{msg}'
        )

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        log_channel = self.bot.get_channel(785146879004508171)
        await log_channel.send(
            f'[{Time.get_info("whole")}][ON ERROR]{traceback.format_exc()}[{args}][{kwargs}][{event}]'
        )

    @commands.Cog.listener()
    async def on_command(self, ctx):
        cmd_name = ctx.command.name
        cmd_parents = ctx.command.full_parent_name

        if isinstance(ctx.channel, discord.DMChannel):
            channel_name = 'user dm_channel'
        else:
            channel_name = ctx.channel.name
        user_name = ctx.author.name
        user_id = ctx.author.id
        message = ctx.message.content

        if not cmd_parents:
            cmd_parents = str('N/A')

        log_msg: str = (
            f'[{cmd_parents}][{cmd_name}], '
            f'[{channel_name}], '
            f'[{user_name}][{user_id}]\n'
            f'[{message}]\n'
        )

        full_log = f'[cmd exec]{log_msg}[{Time.get_info("whole")}]'

        log_json = JsonApi.get('CmdLogging')
        log_json['logs'].append(full_log)
        JsonApi.put('CmdLogging', log_json)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
