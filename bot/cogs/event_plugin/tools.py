from discord.ext import commands
from ...core.cog_config import CogExtension
import discord


class TextPermission(CogExtension):
    @commands.group()
    async def textperm(self, ctx):
        pass

    @textperm.command(aliases=['add'])
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
        await ctx.send(f':white_check_mark: 已將 {member.display_name} 加進此頻道！')

    @textperm.command(aliases=['remove'])
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
        await ctx.send(f':white_check_mark: 已將 {member.display_name} 移出此頻道！')
