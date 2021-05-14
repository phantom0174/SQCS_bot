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
        dyn_json = JsonApi().get('DynamicSetting')

        if channel_id != -1:
            target_channel = ctx.guild.get_channel(channel_id)
            if target_channel is None:
                return await ctx.send(f':x: 沒有id為 {channel_id} 的頻道存在！')

            dyn_json['channel_in_protect'].append(channel_id)
            await ctx.send(f':white_check_mark: 頻道 {target_channel.name} 開啟了保護模式！')
        else:
            dyn_json['channel_in_protect'].append(ctx.channel.id)
            await ctx.send(f':white_check_mark: 頻道 {ctx.channel.name} 開啟了保護模式！')

        JsonApi().put('DynamicSetting', dyn_json)

    @cha.command(aliases=['d'])
    async def disarm(self, ctx, channel_id: int = -1):
        dyn_json = JsonApi().get('DynamicSetting')

        if channel_id != -1:
            target_channel = ctx.guild.get_channel(channel_id)
            if target_channel is None:
                return await ctx.send(f':x: 沒有id為 {channel_id} 的頻道存在！')

            dyn_json['channel_in_protect'].remove(channel_id)
            await ctx.send(f':white_check_mark: 頻道 {target_channel.name} 已解除保護！')
        else:
            dyn_json['channel_in_protect'].remove(ctx.channel.id)
            await ctx.send(f':white_check_mark: 頻道 {ctx.channel.name} 已解除保護！')

        JsonApi().put('DynamicSetting', dyn_json)

    @cha.command(aliases=['p_all'])
    async def protect_all(self, ctx):
        dyn_json = JsonApi().get('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id not in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].append(channel.id)

        JsonApi().put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @cha.command(aliases=['d_all'])
    async def disarm_all(self, ctx):
        dyn_json = JsonApi().get('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].remove(channel.id)

        JsonApi().put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @cha.command(aliases=['cpl'])
    async def clear_protect_list(self, ctx):
        dyn_json = JsonApi().get('DynamicSetting')
        dyn_json['channel_in_protect'].clear()

        JsonApi().put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        dyn_json = JsonApi().get('DynamicSetting')

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
            await respawn_channel.send(':exclamation: 這個頻道被重新生成了')
            entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
            await respawn_channel.send(
                f'由 {entry.user.mention} 於 {delete_time}　刪除'
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
        JsonApi().put('DynamicSetting', dyn_json)


def setup(bot):
    bot.add_cog(Channel(bot))
