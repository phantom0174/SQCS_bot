from discord.ext import commands
from core.classes import CogExtension, JsonApi
import asyncio


class Voice(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def voice(self, ctx):
        pass

    @voice.command()
    async def kick_timer(self, ctx, channel_id: int, countdown: int):  # remove member in voice channel
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
    async def norm(self, ctx, channel_id: int, mode: int):
        protect_target_channel = ctx.guild.get_channel(channel_id)
        await protect_target_channel.set_permissions(ctx.guild.default_role, connect=bool(mode))

    @voice.command()
    @commands.has_any_role('總召', 'Administrator')
    async def collect_on(self, ctx, channel_id: int):
        target_channel = ctx.guild.get_channel(channel_id)
        if target_channel is None:
            return await ctx.send(
                ':exclamation: There exists no such channel'
            )

        dyn_json = JsonApi().get_json('DynamicSetting')

        if channel_id in dyn_json["voice_in_protect"]:
            return await ctx.send(
                f':exclamation: {target_channel.name} is already in collect mode'
            )

        dyn_json["voice_in_protect"].append(channel_id)
        JsonApi().put_json('DynamicSetting', dyn_json)
        for member in ctx.guild.members:
            if member.voice is None:
                continue

            if member.voice.channel != target_channel:
                try:
                    await member.move_to(target_channel)
                except:
                    pass

        await ctx.send(':white_check_mark: Operation finished!')

    @voice.command()
    @commands.has_any_role('總召', 'Administrator')
    async def collect_off(self, ctx, channel_id: int):
        target_channel = ctx.guild.get_channel(channel_id)
        if target_channel is None:
            return await ctx.send(
                ':exclamation: There exists no such channel'
            )

        dyn_json = JsonApi().get_json('DynamicSetting')

        if channel_id not in dyn_json["voice_in_protect"]:
            return await ctx.send(
                f':exclamation: {target_channel.name} is already out of collect mode'
            )

        dyn_json["voice_in_protect"].remove(channel_id)
        JsonApi().put_json('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: Operation finished!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_in_protect = JsonApi().get_json('DynamicSetting')["voice_in_protect"]

        if before.channel is not None and after.channel != before.channel and before.channel.id in voice_in_protect:
            await member.move_to(before.channel)


def setup(bot):
    bot.add_cog(Voice(bot))