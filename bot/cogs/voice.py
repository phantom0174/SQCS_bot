import discord
from discord.ext import commands
from ..core.cog_config import CogExtension
import asyncio


class Voice(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def voice(self, ctx):
        pass

    # remove member in voice channel
    @voice.command()
    async def timer(self, ctx, channel_id: int, countdown: int):
        """cmd
        在 <countdown>秒後將 語音頻道<channel_id> 中的所有成員移出。

        .channel_id: 語音頻道的Discord id
        .countdown: 倒數的時間
        """
        countdown_duration = countdown
        voice_channel = self.bot.get_channel(channel_id)

        def content(s):
            return f':exclamation: 所有成員將在 {s} 秒後被移出 {voice_channel.name}'

        message = await ctx.send(content(countdown_duration))
        while countdown_duration > 0:
            await message.edit(content=content(countdown_duration))
            await asyncio.sleep(1)
            countdown_duration -= 1

        await message.delete()

        for member in voice_channel.members:
            await member.move_to(None)

    @voice.command()
    @commands.has_any_role('總召', 'Administrator')
    async def default_role_connect(self, ctx, channel_id: int, mode: int):
        """cmd
        將 語音頻道<channel_id> 設置為普通成員 可/否 連結

        .channel_id: 語音頻道的id
        .mode: 1 -> 可； 0 -> 不可
        """
        protect_target_channel = ctx.guild.get_channel(channel_id)
        await protect_target_channel.set_permissions(ctx.guild.default_role, connect=bool(mode))


class GroupVCChannel(CogExtension):
    # dynamic creating personal voice channel
    @commands.group()
    async def personal(self, ctx):
        pass

    @personal.command(aliases=['make'])
    async def make_channel(self, ctx, members: commands.Greedy[discord.Member]):
        """cmd
        在語音終端機時使用指令，便可為 成員們<members> 創立私人語音包廂。

        .members: 一次性@所有要加入的成員
        """
        terminal_channel = ctx.guild.get_channel(839170475309006979)

        if ctx.author.voice.channel != terminal_channel:
            return await ctx.send(f':x: 請先加入 {terminal_channel.name} 以使用這個指令！')

        make_channel = await ctx.guild.create_voice_channel(
            name=f"{members[0].display_name}'s party",
            category=terminal_channel.category
        )

        for member in members:
            if member.voice.channel is None:
                continue

            perms = {
                "connect": True,
                "request_to_speak": True,
                "speak": True,
                "stream": True,
                "use_voice_activation": True
            }
            await make_channel.set_permissions(member, **perms)
            await member.move_to(make_channel)

        await make_channel.set_permissions(ctx.guild.default_role, connect=False)
        await ctx.send(f':white_check_mark: 已創建頻道 {make_channel.name}！')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel is None or before.channel == after.channel:
            return

        if not before.channel.name.endswith('party'):
            return

        if before.channel.name == f"{member.display_name}'s party":
            await before.channel.delete()

        if not before.channel.members:
            await before.channel.delete()


def setup(bot):
    bot.add_cog(Voice(bot))
