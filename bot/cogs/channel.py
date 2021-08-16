import discord
from discord.ext import commands
from ..core.cog_config import CogExtension
from ..core.utils import Time
from ..core.db.jsonstorage import JsonApi


class Protect(CogExtension):
    @commands.group(aliases=['p'])
    @commands.has_any_role('總召', 'Administrator')
    async def protect(self, ctx):
        pass

    @protect.command()
    async def on(self, ctx, channel_id: int = -1):
        """cmd
        開啟 頻道<channel_id> 的保護模式，如果沒有輸入代表目前的頻道。

        .channel_id: Discord 中頻道的id
        """
        dyn_json = JsonApi.get('DynamicSetting')

        if channel_id != -1:
            target_channel = ctx.guild.get_channel(channel_id)
            if target_channel is None:
                return await ctx.send(f':x: 沒有id為 {channel_id} 的頻道存在！')

            dyn_json['channel_in_protect'].append(channel_id)
            await ctx.send(f':white_check_mark: 頻道 {target_channel.name} 開啟了保護模式！')
        else:
            dyn_json['channel_in_protect'].append(ctx.channel.id)
            await ctx.send(f':white_check_mark: 頻道 {ctx.channel.name} 開啟了保護模式！')

        JsonApi.put('DynamicSetting', dyn_json)

    @protect.command()
    async def off(self, ctx, channel_id: int = -1):
        """cmd
        關閉 頻道<channel_id> 的保護模式，如果沒有輸入代表目前的頻道。

        .channel_id: Discord 中頻道的id
        """
        dyn_json = JsonApi.get('DynamicSetting')

        if channel_id != -1:
            target_channel = ctx.guild.get_channel(channel_id)
            if target_channel is None:
                return await ctx.send(f':x: 沒有id為 {channel_id} 的頻道存在！')

            dyn_json['channel_in_protect'].remove(channel_id)
            await ctx.send(f':white_check_mark: 頻道 {target_channel.name} 已解除保護！')
        else:
            dyn_json['channel_in_protect'].remove(ctx.channel.id)
            await ctx.send(f':white_check_mark: 頻道 {ctx.channel.name} 已解除保護！')

        JsonApi.put('DynamicSetting', dyn_json)

    @protect.command()
    async def all_on(self, ctx):
        """cmd
        開啟伺服器中所有頻道的保護模式。
        """
        dyn_json = JsonApi.get('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id not in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].append(channel.id)

        JsonApi.put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @protect.command()
    async def all_off(self, ctx):
        """cmd
        關閉伺服器中所有頻道的保護模式。
        """
        dyn_json = JsonApi.get('DynamicSetting')

        for channel in ctx.guild.channels:
            if channel.id in dyn_json['channel_in_protect']:
                dyn_json['channel_in_protect'].remove(channel.id)

        JsonApi.put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @protect.command(aliases=['cpl'])
    async def clear_list(self, ctx):
        """cmd
        清除資料庫中的頻道保護列表。
        """
        dyn_json = JsonApi.get('DynamicSetting')
        dyn_json['channel_in_protect'].clear()

        JsonApi.put('DynamicSetting', dyn_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        dyn_json = JsonApi.get('DynamicSetting')

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
                f'由 {entry.user.mention} 於 {delete_time} 刪除'
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
        JsonApi.put('DynamicSetting', dyn_json)


class Meeting(CogExtension):
    # for text and voice meeting usage
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def meeting(self, ctx):
        pass

    # for voice meeting usage
    @meeting.command(aliases=['shit!'])
    async def on(self, ctx, channel_id: int):
        """cmd
        開啟 語音頻道<channel_id> 的開會模式。

        .channel_id: Discord 中頻道的id
        """
        target_channel = ctx.guild.get_channel(channel_id)
        if target_channel is None:
            return await ctx.send(':x: 這是一個無效頻道！')

        dyn_json = JsonApi.get('DynamicSetting')

        if channel_id in dyn_json["voice_in_meeting"]:
            return await ctx.send(f':x: 頻道 {target_channel.name} 已在開會模式中！')

        dyn_json["voice_in_meeting"].append(channel_id)
        JsonApi.put('DynamicSetting', dyn_json)

        await target_channel.set_permissions(ctx.guild.default_role, connect=False)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @meeting.command()
    async def off(self, ctx, channel_id: int):
        """cmd
        關閉 語音頻道<channel_id> 的開會模式。

        .channel_id: Discord 中頻道的id
        """
        target_channel = ctx.guild.get_channel(channel_id)
        if target_channel is None:
            return await ctx.send(':x: 這是一個無效頻道！')

        dyn_json = JsonApi.get('DynamicSetting')

        if channel_id not in dyn_json["voice_in_meeting"]:
            return await ctx.send(f':x: 頻道 {target_channel.name} 不在開會模式中！')

        dyn_json["voice_in_meeting"].remove(channel_id)
        JsonApi.put('DynamicSetting', dyn_json)

        await target_channel.set_permissions(ctx.guild.default_role, connect=True)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel == before.channel:
            return

        if before.channel is None:
            return

        meeting_list = JsonApi.get('DynamicSetting')["voice_in_meeting"]
        if before.channel.id in meeting_list:
            await member.move_to(before.channel)


def setup(bot):
    bot.add_cog(Protect(bot))
    bot.add_cog(Meeting(bot))
