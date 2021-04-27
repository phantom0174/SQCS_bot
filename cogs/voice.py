from discord.ext import commands
from core.classes import CogExtension
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


def setup(bot):
    bot.add_cog(Voice(bot))