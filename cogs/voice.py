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
    async def protect_add(self, ctx, channel_id: int):
        dyn_json = JsonApi().get_json('DynamicSetting')

        if channel_id in dyn_json["voice_in_protect"]:
            return await ctx.send(
                ':exclamation: The channel is already in protection;\n'
                'or there exists no channel with this id'
            )

        dyn_json["voice_in_protect"].append(channel_id)
        JsonApi().put_json('DynamicSetting', dyn_json)

    @voice.command()
    async def protect_remove(self, ctx, channel_id: int):
        dyn_json = JsonApi().get_json('DynamicSetting')

        if channel_id not in dyn_json["voice_in_protect"]:
            return await ctx.send(
                ':exclamation: The channel is already out of protection;\n'
                'or there exists no channel with this id'
            )

        dyn_json["voice_in_protect"].remove(channel_id)
        JsonApi().put_json('DynamicSetting', dyn_json)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        voice_in_protect = JsonApi().get_json('DynamicSetting')["voice_in_protect"]

        if after.channel is not None and after.channel.id in voice_in_protect:
            await member.move_to(None)


def setup(bot):
    bot.add_cog(Voice(bot))