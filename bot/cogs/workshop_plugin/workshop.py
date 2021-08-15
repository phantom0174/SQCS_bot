from discord.ext import commands
import discord
from ...core.utils import DiscordExt
from ...core.cog_config import CogExtension


# This extension is currently not in use.


class WorkShop(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def ws(self, ctx):
        pass

    @ws.command()
    async def snapshot(self, ctx, voice_id: int):
        """cmd
        將 語音頻道<voice_id> 設定為目前在頻道中的成員所屬。

        .voice_id: 語音頻道的id
        """
        voice_channel: discord.VoiceChannel = ctx.guild.get_channel(voice_id)
        voice_perms = {
            "connect": True,
            "request_to_speak": True,
            "speak": True,
            "stream": True,
            "use_voice_activation": True
        }
        member_list = ''
        for member in voice_channel.members:
            member_list += f'{member.display_name}({member.id})\n'

            # text perm setting
            text_perms = ctx.channel.overwrites_for(member)

            text_perms.view_channel = True
            text_perms.read_messages = True
            text_perms.add_reactions = True
            text_perms.send_messages = True
            text_perms.read_message_history = True
            text_perms.attach_files = True
            text_perms.embed_links = True

            await ctx.channel.set_permissions(member, overwrite=text_perms)

            # voice perm setting
            await voice_channel.set_permissions(member, **voice_perms)

        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await voice_channel.set_permissions(ctx.guild.default_role, connect=False, view_channel=False)
        await ctx.send(embed=await DiscordExt.create_embed(
            f'Team {voice_channel.name}',
            'default',
            discord.Colour.dark_blue(),
            ['Members'],
            [member_list]
        ))


def setup(bot):
    bot.add_cog(WorkShop(bot))
