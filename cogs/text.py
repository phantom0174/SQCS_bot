from discord.ext import commands
from core.cog_config import CogExtension
import discord
from core.db import JsonApi
import asyncio


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
        await ctx.send(f':white_check_mark: 已將 {member.display_name} 加進此頻道！')

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
        await ctx.send(f':white_check_mark: 已將 {member.display_name} 移出此頻道！')

    # for meeting usage
    @commands.group(aliases=['meeting'])
    async def text_meeting(self, ctx):
        pass

    @text_meeting.command()
    async def join(self, ctx):
        if ctx.author.voice.channel is None:
            return await ctx.send(
                content=':x: 請先加入與此頻道連結的語音頻道！',
                delete_after=5
            )

        dyn_json = JsonApi().get('DynamicSetting')

        find = bool(False)
        bind_voice_channel = None
        for item in dyn_json['text_voice_channel_in_binding']:
            if item['text_channel'] == ctx.channel.id:
                find = True
                bind_voice_channel = ctx.guild.get_channel(item['voice_channel'])
                break

        if not find:
            return await ctx.send(content=':x: 此頻道尚未與語音頻道連結！', delete_after=5)

        permit_msg = await ctx.send(content=f':question: 請問管理者是否接受申請？（剩餘 30 秒）')
        await permit_msg.add_reaction('⭕')
        await permit_msg.add_reaction('❌')

        def is_admin(member: discord.Member):
            member_roles_name = [role.name for role in member.roles]
            if '總召' in member_roles_name or 'Administrator' in member_roles_name:
                return True
            return False

        def check(check_reaction, check_user):
            return check_reaction.message.id == permit_msg.id and is_admin(check_user)

        try:
            asyncio.ensure_future(permit_countdown(permit_msg, 30))
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=30.0)

            if reaction.emoji == '⭕':
                await ctx.author.move_to(bind_voice_channel)
            elif reaction.emoji == '❌':
                await ctx.author.move_to(None)

            return await permit_msg.delete()
        except asyncio.TimeoutError:
            return await permit_msg.delete()


async def permit_countdown(target_msg, sec):
    def content(s):
        return f':question: 請問管理者是否接受申請？（剩餘 {s} 秒）'

    while sec:
        try:
            await target_msg.edit(content=content(sec))
            await asyncio.sleep(1)
            sec -= 1
        except:
            break


def setup(bot):
    bot.add_cog(Text(bot))
