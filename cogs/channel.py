from discord.ext import commands
from core.classes import CogExtension, JsonApi
import discord


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

        respawn_channel = await channel.guild.create_text_channel(
            name=channel.name,
            category=channel.category,
            overwrites=channel.overwrites
        )
        dyn_json['channel_in_protect'].remove(channel.id)
        dyn_json['channel_in_protect'].append(respawn_channel.id)
        JsonApi().put_json('DynamicSetting', dyn_json)

        await respawn_channel.send(':exclamation: The channel has been respawned')
        entry = await channel.guild.audit_logs(action=discord.AuditLogAction.channel_delete, limit=1).get()
        await respawn_channel.send(
            f'Deleted by {entry.user.mention} at {entry.created_at}'
        )


def setup(bot):
    bot.add_cog(Channel(bot))