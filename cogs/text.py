from discord.ext import commands
from core.classes import CogExtension
import discord


class Text(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def text(self, ctx):
        pass

    @text.command()
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