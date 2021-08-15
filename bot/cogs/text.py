import discord
from discord.ext import commands
from ..core.cog_config import CogExtension


class Text(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def text(self, ctx):
        pass

    # delete message
    @text.command()
    async def clear(self, ctx, msg_id: int):
        """cmd
        從目前的訊息往上刪除至 訊息<msg_id>

        .msg_id: 訊息在Discord中的id
        """
        find = bool(False)
        while not find:
            msg_logs = await ctx.channel.history(limit=50).flatten()
            for msg in msg_logs:
                await msg.delete()
                if msg.id == msg_id:
                    find = True
                    break

    @text.command(aliases=['move'])
    async def trans(self, ctx, start_id: int, end_id: int, to_channel: discord.TextChannel):
        msg_logs = await ctx.channel.history(limit=500).flatten()
        msg_logs.reverse()

        interval = bool(False)
        for msg in msg_logs:
            if msg.id == start_id:
                interval = True

            if interval and msg.content != '':
                author_icon_url = msg.author.avatar_url_as(size=32)
                embed = discord.Embed()
                embed.set_thumbnail(url=author_icon_url)
                embed.add_field(name=msg.author.display_name, value=msg.content)
                await to_channel.send(embed=embed)

                await msg.delete()

            if msg.id == end_id:
                break


def setup(bot):
    bot.add_cog(Text(bot))
