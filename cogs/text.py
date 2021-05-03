from discord.ext import commands
from core.classes import CogExtension
import discord


class Text(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def text(self, ctx):
        pass

    # delete message
    @text.command()
    async def clear(self, ctx, msg_id: int):
        find = bool(False)
        while not find:
            msg_logs = await ctx.channel.history(limit=50).flatten()
            for msg in msg_logs:
                await msg.delete()
                if msg.id == msg_id:
                    find = bool(True)
                    break

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

    @text.command(aliases=['add'])
    async def add_member(self, ctx, member: discord.Member):
        perms = ctx.channel.overwrites_for(member)

        perms.view_channel = True
        perms.read_messages = True
        perms.add_reactions = True
        perms.send_messages = True
        perms.read_message_history = True
        perms.attach_files = True
        perms.embed_links = True

        await ctx.channel.set_permissions(member, overwrite=perms)
        await ctx.send(
            f':white_check_mark: Successfully added {member.display_name} to this channel!'
        )

    @text.command(aliases=['remove'])
    async def remove_member(self, ctx, member: discord.Member):
        perms = ctx.channel.overwrites_for(member)

        perms.view_channel = None
        perms.read_messages = None
        perms.add_reactions = None
        perms.send_messages = None
        perms.read_message_history = None
        perms.attach_files = None
        perms.embed_links = None

        await ctx.channel.set_permissions(member, overwrite=perms)
        await ctx.send(
            f':white_check_mark: Successfully removed {member.display_name} from this channel!'
        )


def setup(bot):
    bot.add_cog(Text(bot))