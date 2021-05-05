from discord.ext import commands
from core.utils import Time
from core.cog_config import CogExtension, JsonApi


class Event(CogExtension):

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

        log_msg: str = (
            f'[{cmd_parents}][{cmd_name}], '
            f'[{channel_name}], '
            f'[{user_name}][{user_id}]\n'
            f'[{message}]\n'
        )

        full_log = f'[cmd exec]{log_msg}[{Time.get_info("whole")}]'

        log_json = JsonApi().get_json('CmdLogging')
        log_json['logs'].append(full_log)
        JsonApi().put_json('CmdLogging', log_json)


def setup(bot):
    bot.add_cog(Event(bot))
