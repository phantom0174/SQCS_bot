import discord
from discord.ext import commands
from ..core.cog_config import CogExtension
from ..core.db.jsonstorage import JsonApi
from ..core.db.mongodb import Mongo
from ..core.fluctlight_ext import Fluct
from typing import Union


class KickMember(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def kick(self, ctx):
        pass

    @kick.command()
    async def list(self, ctx):
        """cmd
        列出待踢除名單。
        """
        await ctx.send(content=':hourglass_flowing_sand: 尋找中...', delete_after=3.0)

        kick_cursor = Mongo('sqcs-bot').get_cur('ReadyToKick')
        data = kick_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':x: 待踢除名單為空！')

        kick_member_list = ''
        for member in data:

            member_info: str = (
                f'Id: {member["_id"]},'
                f'Name: {member["name"]},'
                f'Contrib: {member["contrib"]},'
                f'lvl_ind: {member["lvl_ind"]}\n'
            )

            kick_member_list += member_info
            if len(kick_member_list) > 1600:
                await ctx.send(kick_member_list)
                kick_member_list = ''

        if len(kick_member_list) > 0:
            await ctx.send(kick_member_list)

        await ctx.send(':white_check_mark: 記錄尋找完畢！')

    @kick.command(aliases=['insert'])
    async def add(self, ctx, target_member: Union[discord.Member, int]):
        """cmd
        將 成員<target_member> 加入待踢除名單。

        .target_member: 可直接標註成員，或是成員在Discord中的id
        """
        if isinstance(target_member, discord.Member):
            member_id = target_member.id
        else:
            member_id = target_member

        fluctlight_cursor = Mongo('LightCube').get_cur('MainFluctlights')
        data = fluctlight_cursor.find_one({"_id": member_id})

        if not data:
            return await ctx.send(f':x: 沒有成員 {target_member} 的搖光資料！')

        member_info = {
            "_id": member_id,
            "name": data["name"],
            "contrib": data["contrib"],
            "lvl_ind": data["lvl_ind"]
        }
        kick_cursor = Mongo('sqcs-bot').get_cur('ReadyToKick')
        kick_cursor.insert_one(member_info)

        await ctx.send(f':white_check_mark: 成員 {data["name"]} - {member_id} 已被加到待踢除名單！')

    @kick.command(aliases=['delete', 'del'])
    async def remove(self, ctx, target_member: Union[discord.Member, int]):
        """cmd
        將 成員<target_member> 移出待踢除名單。

        .target_member: 可直接標註成員，或是成員在Discord中的id
        """
        if isinstance(target_member, discord.Member):
            member_id = target_member.id
        else:
            member_id = target_member

        kick_cursor = Mongo('sqcs-bot').get_cur('ReadyToKick')
        data = kick_cursor.find_one({"_id": member_id})

        if not data:
            return await ctx.send(f':x: 成員 {member_id} 不在待踢除名單中！')

        kick_cursor.delete_one({"_id": member_id})

        await ctx.send(f':white_check_mark: 已將成員 {data["name"]} - {member_id} 從待踢除名單中移除！')

    @kick.command(aliases=['single'])
    async def kick_single(self, ctx, target_member: Union[discord.Member, int], kick_reason: str):
        """cmd
        將 成員<target_member> 踢除（需要在待踢除名單中）。

        .target_member: 可直接標註成員，或是成員在Discord中的id
        .kick_reason: 踢除原因
        """
        if isinstance(target_member, discord.Member):
            member_id = target_member.id
        else:
            member_id = target_member

        kick_cursor = Mongo('sqcs-bot').get_cur('ReadyToKick')
        data = kick_cursor.find_one({"_id": member_id})

        if not data:
            return await ctx.send(f':x: 成員 {member_id} 不在待踢除名單中！')

        kick_user = ctx.guild.get_member(member_id)

        if kick_reason == 'default':
            kick_reason = f':skull_crossbones: 違反指數達到了 {data["lvl_ind"]}'

        msg = await JsonApi.get_humanity('kick/kick_single', '\n')
        msg += f'> {kick_reason}\n'
        msg += await JsonApi.get_humanity('kick/re_join')

        # no perm to send msg to user via server
        try:
            await kick_user.send(msg)
        except BaseException:
            pass

        try:
            await kick_user.kick(reason=kick_reason)

            fluct_ext = Fluct(member_id=member_id)
            await fluct_ext.delete_main()
            await fluct_ext.delete_vice()

            kick_cursor.delete_one({"_id": member_id})
            await ctx.send(f':white_check_mark: 成員 {data["name"]} - {data["_id"]} 已被踢除！')
        except Exception as e:
            await ctx.send(f':x: 踢除 {data["name"]} - {data["_id"]} 時發生了錯誤！')
            await ctx.send(content=e, delete_after=5.0)

    @kick.command(aliases=['all'])
    async def kick_all(self, ctx):
        """cmd
        將所有在踢除名單中的成員踢除。
        """
        kick_cursor = Mongo('sqcs-bot').get_cur('ReadyToKick')
        data = kick_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':x: 待踢除名單為空！')

        fluct_ext = Fluct()
        for member in data:
            kick_user = ctx.guild.get_member(member["_id"])

            msg = await JsonApi.get_humanity('kick/kick_all', '\n')
            msg += f'> Levelling index reached {member["lvl_ind"]}.\n'
            msg += await JsonApi.get_humanity('kick/re_join')

            # no perm to send msg to user via server
            try:
                await kick_user.send(msg)
            except BaseException:
                pass

            try:
                await kick_user.kick(reason=f'違反指數達到了 {member["lvl_ind"]}')

                await fluct_ext.delete_main(member["_id"])
                await fluct_ext.delete_vice(member["_id"])
            except Exception as e:
                await ctx.send(f':x: 踢除 {member["name"]} - {member["_id"]} 時發生了錯誤！')
                await ctx.send(content=e, delete_after=5.0)

        kick_cursor.delete_many({})
        await ctx.send(':white_check_mark: 所有在待踢除名單中的成員已被踢除！')


class NT(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def nt(self, ctx):
        pass

    @commands.command()
    async def list(self, ctx):
        """cmd
        列出黑名單。
        """
        id_list = JsonApi.get('NT')["id_list"]
        await ctx.send(id_list)

    @commands.command(aliases=['push', 'insert'])
    async def add(self, ctx, user_id: int = None):
        """cmd
        將 成員<user_id> 加入黑名單。

        .user_id: 成員的Discord id
        """
        nt_json = JsonApi.get('NT')
        if user_id is None:
            return

        nt_json['id_list'].append(user_id)
        JsonApi.put('NT', nt_json)
        await ctx.send(':white_check_mark: 指令執行完畢！')


def setup(bot):
    bot.add_cog(KickMember(bot))
    bot.add_cog(NT(bot))
