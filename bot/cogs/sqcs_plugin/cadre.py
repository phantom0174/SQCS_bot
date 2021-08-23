from discord.ext import commands
import os
from ...core.cog_config import CogExtension
from ...core.db.jsonstorage import JsonApi
from ...core.db.mongodb import Mongo
from ...core.utils import Time
import discord


class Cadre(CogExtension):

    @commands.group()
    async def ca(self, ctx):
        pass

    @ca.command()
    async def apply(self, ctx, cadre: str):
        """cmd
        於幹部申請區申請 幹部<cadre>

        .cadre: 可為SQCS現在有的幹部部門
        """
        cadre_set_cursor, cadre_cursor = Mongo('sqcs-bot').get_curs(['CadreSetting', 'Cadre'])

        cadre_setting = cadre_set_cursor.find_one({"_id": 0})
        if ctx.channel.id != cadre_setting['apply_channel']:
            return

        cadre_options = cadre_setting['apply_options']
        if cadre not in cadre_options:
            return await ctx.send(
                content=f':x: 職位選項必須要在 {cadre_options} 中！',
                delete_after=8
            )

        data = cadre_cursor.find_one({"_id": ctx.author.id})

        if data:
            return await ctx.author.send(
                f':x: {ctx.author.mention} (id: {data["_id"]})\n'
                f':scroll: 你已經於 {data["apply_time"]} 申請 `{data["apply_cadre"]}` 職位\n'
                f'> 請確認是否發生 `重複申請` `同時申請兩職位` `申請錯誤`\n'
                f'> 如有疑問，請洽總召'
            )

        apply_time = Time.get_info('whole')
        apply_info = {
            "_id": ctx.author.id,
            "name": ctx.author.display_name,
            "apply_cadre": cadre,
            "apply_time": apply_time
        }

        cadre_cursor.insert_one(apply_info)

        # no perm to send msg to user via server
        try:
            await ctx.author.send(
                f':white_check_mark: 我收到你的申請了！請耐心等待審核\n'
                f'申請人名字：{ctx.author.display_name},\n'
                f'申請人id：{ctx.author.id},\n'
                f'申請職位：{cadre},\n'
                f'申請時間：{apply_time}'
            )
        except BaseException:
            pass

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        """cmd
        列出現在的所有幹部申請。
        """
        cadre_cursor = Mongo('sqcs-bot').get_cur('Cadre')
        data = cadre_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':x: 職位申請名單為空！')

        apply_info = ''
        for item in data:
            apply_info += (
                f'{item["name"]}({item["_id"]}): '
                f'{item["apply_cadre"]}, '
                f'{item["apply_time"]}\n'
            )

            if len(apply_info) > 1600:
                await ctx.send(apply_info)
                apply_info = ''

        if len(apply_info) > 0:
            # no perm to send msg to user via server
            try:
                await ctx.author.send(apply_info)
            except BaseException:
                pass

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def permit(self, ctx, permit_id: int):
        """cmd
        批准 成員<permit_id> 的幹部申請。

        .permit_id: 要批准成員的Discord id
        """
        cadre_cursor = Mongo('sqcs-bot').get_cur('Cadre')
        data = cadre_cursor.find_one({"_id": permit_id})

        if not data:
            return await ctx.send(f':x: 申請名單中沒有id為 {permit_id} 的申請！')

        # no perm to send msg to user via server
        try:
            await ctx.author.send(
                f':white_check_mark: 你已批准 {data["name"]} 對職位 {data["apply_cadre"]} 的申請！'
            )
        except BaseException:
            pass

        member = ctx.guild.get_member(data["_id"])

        # no perm to send msg to user via server
        try:
            await member.send(
                f':white_check_mark: 你於 {data["apply_time"]} 申請 {data["apply_cadre"]} 的程序已通過！\n'
                f'此為幹部群的連結，請在加入之後使用指令領取屬於你的身分組\n'
                f'{os.environ.get("WORKING_DC_GUILD_LINK")}'
            )
        except BaseException:
            pass

        cadre_cursor.delete_one({"_id": data["_id"]})

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def search(self, ctx, search_id: int):
        """cmd
        查詢 成員<permit_id> 的幹部申請。

        .permit_id: 要查詢成員的Discord id
        """
        cadre_cursor = Mongo('sqcs-bot').get_cur('Cadre')
        data = cadre_cursor.find_one({"_id": search_id})

        if not data:
            return await ctx.send(f':x: 申請名單中沒有id為 {search_id} 的申請！')

        await ctx.send(
            f'{data["name"]}({data["_id"]}): '
            f'{data["apply_cadre"]}, '
            f'{data["apply_time"]}'
        )

    @ca.command(aliases=['delete'])
    @commands.has_any_role('總召', 'Administrator')
    async def remove(self, ctx, delete_id: int):
        """cmd
        移除 成員<permit_id> 的幹部申請。

        .permit_id: 要移除的成員之Discord id
        """
        cadre_cursor = Mongo('sqcs-bot').get_cur('Cadre')
        data = cadre_cursor.find_one({"_id": delete_id})

        if not data:
            return await ctx.send(f':x: 申請名單中沒有id為 {delete_id} 的申請！')

        cadre_cursor.delete_one({"_id": delete_id})
        await ctx.send(f':white_check_mark: 成員 {data["name"]}({delete_id}) 的申請已被刪除！')


# need to be fixed!
class GuildRole(CogExtension):
    @commands.group(aliases=['rl'])
    @commands.has_any_role('總召', 'Administrator')
    async def role_level(self, ctx):
        pass

    @role_level.command()
    async def init(self, ctx):
        default_role = ctx.guild.get_role(743654256565026817)
        new_default_role = ctx.guild.get_role(823803958052257813)

        for member in ctx.guild.members:
            if member.bot:
                continue

            if default_role in member.roles:
                try:
                    await member.remove_roles(default_role)
                    await member.add_roles(new_default_role)
                except BaseException:
                    pass

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @role_level.command()
    async def init_single(self, ctx, member: discord.Member):
        default_role = ctx.guild.get_role(823803958052257813)

        for role in member.roles:
            if role.name != '@everyone':
                await member.remove_roles(role)

        await member.add_roles(default_role)
        await ctx.send(':white_check_mark: 指令執行完畢！')

    @role_level.command()
    async def advance(self, ctx, member: discord.Member):
        if member not in ctx.guild.members:
            return await ctx.send(f':x: 不存在成員 {member.display_name}！')

        sta_json = JsonApi.get('StaticSetting')
        name_to_index: dict = sta_json['level_role_id']

        current_roles = member.roles
        for role in current_roles:
            if role.name in name_to_index.keys():

                name_to_index: dict = sta_json['level_role_name_to_index']
                index_to_name: dict = sta_json['level_role_index_to_name']
                advance_index = int(name_to_index.get(role.name)) + 1
                new_role_name = index_to_name.get(str(advance_index))
                new_role = ctx.guild.get_role(name_to_index.get(new_role_name))

                await member.remove_roles(role)
                await member.add_roles(new_role)
                break

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @role_level.command()
    async def retract(self, ctx, member: discord.Member):
        if member not in ctx.guild.members:
            return await ctx.send(f':x: 不存在成員 {member.display_name}！')

        sta_json = JsonApi.get('StaticSetting')
        name_to_index: dict = sta_json['level_role_id']

        current_roles = member.roles
        for role in current_roles:
            if role.name in name_to_index.keys():
                name_to_index: dict = sta_json['level_role_name_to_index']
                index_to_name: dict = sta_json['level_role_index_to_name']
                advance_index = int(name_to_index.get(role.name)) - 1
                new_role_name = index_to_name.get(str(advance_index))
                new_role = ctx.guild.get_role(name_to_index.get(new_role_name))

                await member.remove_roles(role)
                await member.add_roles(new_role)
                break

        await ctx.send(':white_check_mark: 指令執行完畢！')


def setup(bot):
    bot.add_cog(Cadre(bot))
    bot.add_cog(GuildRole(bot))
