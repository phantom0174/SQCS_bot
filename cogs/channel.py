from discord.ext import commands
from core.cog_config import CogExtension
import discord
from core.utils import Time
from core.db import JsonApi


class Channel(CogExtension):
    @commands.group(aliases=['cha_p', 'protect'])
    @commands.has_any_role('總召', 'Administrator')
    async def cha_protect(self, ctx):
        pass

    @cha_protect.command()
    async def on(self, ctx, channel_id: int = -1):
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

    @cha_protect.command()
    async def off(self, ctx, channel_id: int = -1):
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

    @cha_protect.command()
    async def all_on(self, ctx):
        dyn_json = JsonApi().get('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id not in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].append(channel.id)

        JsonApi().put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @cha_protect.command()
    async def all_off(self, ctx):
        dyn_json = JsonApi().get('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].remove(channel.id)

        JsonApi().put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @cha_protect.command(aliases=['cpl'])
    async def clear_list(self, ctx):
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

    @commands.group()
    async def cha_bind(self, ctx):
        pass

    @cha_bind.command(aliases=['create', 'insert'])
    async def add(self, ctx, text_cha_id: int, voice_cha_id: int):
        text_channel = ctx.guild.get_channel(text_cha_id)
        voice_channel = ctx.guild.get_channel(voice_cha_id)

        if text_channel is None or voice_channel is None:
            return await ctx.send(
                ':x: 其中有一個無效頻道！'
            )

        binding_info = {
            "text_channel": text_cha_id,
            "voice_channel": voice_cha_id
        }

        dyn_json = JsonApi().get('DynamicSetting')
        dyn_json['text_voice_channel_in_binding'].append(binding_info)
        JsonApi().put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @cha_bind.command(aliases=['remove'])
    async def delete(self, ctx, text_cha_id: int):
        text_channel = ctx.guild.get_channel(text_cha_id)

        if text_channel is None:
            return await ctx.send(':x: 此為無效頻道！')

        dyn_json = JsonApi().get('DynamicSetting')
        for index, item in enumerate(dyn_json['text_voice_channel_in_binding']):
            if item['text_channel'] == text_channel:
                del dyn_json['text_voice_channel_in_binding'][index]
                break

        JsonApi().put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')


def setup(bot):
    bot.add_cog(Channel(bot))
