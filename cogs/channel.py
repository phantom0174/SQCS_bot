from discord.ext import commands
from core.cog_config import CogExtension
import discord
from core.utils import Time
from core.db import JsonApi


class Channel(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def cha(self, ctx):
        pass

    @cha.command(aliases=['p'])
    async def protect(self, ctx, channel_id: int = -1):
        dyn_json = JsonApi().get_json('DynamicSetting')

        if channel_id != -1:
            target_channel = ctx.guild.get_channel(channel_id)
            if target_channel is None:
                return await ctx.send(f':exclamation: No such channel with id {channel_id} exists')

            dyn_json['channel_in_protect'].append(channel_id)
            await ctx.send(f':white_check_mark: {target_channel.name} is in protect mode!')
        else:
            dyn_json['channel_in_protect'].append(ctx.channel.id)
            await ctx.send(f':white_check_mark: {ctx.channel.name} is in protect mode!')

        JsonApi().put_json('DynamicSetting', dyn_json)

    @cha.command(aliases=['d'])
    async def disarm(self, ctx, channel_id: int = -1):
        dyn_json = JsonApi().get_json('DynamicSetting')

        if channel_id != -1:
            target_channel = ctx.guild.get_channel(channel_id)
            if target_channel is None:
                return await ctx.send(f':exclamation: No such channel with id {channel_id} exists')

            dyn_json['channel_in_protect'].remove(channel_id)
            await ctx.send(f':white_check_mark: {target_channel.name} is in disarm mode!')
        else:
            dyn_json['channel_in_protect'].remove(ctx.channel.id)
            await ctx.send(f':white_check_mark: {ctx.channel.name} is in disarm mode!')

        JsonApi().put_json('DynamicSetting', dyn_json)

    @cha.command(aliases=['p_all'])
    async def protect_all(self, ctx):
        dyn_json = JsonApi().get_json('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id not in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].append(channel.id)

        JsonApi().put_json('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: Operation finished!')

    @cha.command(aliases=['d_all'])
    async def disarm_all(self, ctx):
        dyn_json = JsonApi().get_json('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].remove(channel.id)

        JsonApi().put_json('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: Operation finished!')

    @cha.command(aliases=['cpl'])
    async def clear_protect_list(self, ctx):
        dyn_json = JsonApi().get_json('DynamicSetting')
        dyn_json['channel_in_protect'].clear()

        JsonApi().put_json('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: Operation finished!')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        dyn_json = JsonApi().get_json('DynamicSetting')

        if channel.id not in dyn_json['channel_in_protect']:
            return

        respawn_config = {
            "name": channel.name,
            "category": channel.category,
            "position": channel.position,
            "overwrites": channel.overwrites,
            "permissions_synced": channel.permissions_synced
        }

        if str(channel.type) == 'text':
            delete_time = Time.get_info('whole')

            text_config = {
                "topic": channel.topic
            }
            respawn_channel = await channel.guild.create_text_channel(
                **respawn_config,
                **text_config
            )
            await respawn_channel.send(':exclamation: The channel has been respawned')
            entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
            await respawn_channel.send(
                f'Deleted by {entry.user.mention} at {delete_time}'
            )
        elif str(channel.type) == 'voice':
            voice_config = {
                "bitrate": channel.bitrate,
                "rtc_region": channel.rtc_region,
                "user_limit": channel.user_limit
            }
            respawn_channel = await channel.guild.create_voice_channel(
                **respawn_config,
                **voice_config
            )
        elif str(channel.type) == 'stage_voice':
            stage_config = {
                "bitrate": channel.bitrate,
                "rtc_region": channel.rtc_region,
                "user_limit": channel.user_limit,
                "topic": channel.topic,
                "requesting_to_speak": channel.requesting_to_speak
            }
            respawn_channel = await channel.guild.create_stage_channel(
                **respawn_config,
                **stage_config
            )
        else:
            return

        dyn_json['channel_in_protect'].remove(channel.id)
        dyn_json['channel_in_protect'].append(respawn_channel.id)
        JsonApi().put_json('DynamicSetting', dyn_json)


def setup(bot):
    bot.add_cog(Channel(bot))