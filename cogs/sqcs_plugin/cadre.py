from discord.ext import commands
import os
from core.cog_config import CogExtension
from core.db import self_client
from core.utils import Time


class Cadre(CogExtension):

    @commands.group()
    async def ca(self, ctx):
        pass

    @ca.command()
    async def apply(self, ctx, cadre: str):
        appl = ctx.author  # applicant

        if ctx.channel.id != 774794670034124850:
            return

        if cadre not in ['副召', '網管', '議程', '公關', '美宣', '學術']:
            return await ctx.send(
                content=f':exclamation: {appl.mention}, 沒有名為 `{cadre}` 的職位！', delete_after=5.0
            )

        cadre_cursor = self_client["Cadre"]
        data = cadre_cursor.find_one({"_id": appl.id})

        if data:
            return await appl.send(
                f':exclamation: {appl.mention} (id: {data["_id"]}),\n'
                f'您已經於 {data["apply_time"]} 申請 `{data["apply_cadre"]}` 職位！\n'
                f'請確認是否發生以下狀況 `重複申請` `同時申請兩職位` `申請錯誤`\n'
                f'如有疑問請洽總召'
            )

        apply_time = Time.get_info('whole')
        apply_info = {
            "_id": appl.id,
            "name": appl.display_name,
            "apply_cadre": cadre,
            "apply_time": apply_time
        }

        cadre_cursor.insert_one(apply_info)

        await appl.send(
            f':white_check_mark: 我收到你的申請了！請耐心等待\n'
            f'申請人名字: `{appl.display_name}`,\n'
            f'申請人id: `{appl.id}`,\n'
            f'申請職位: `{cadre}`,\n'
            f'申請時間: `{apply_time}`'
        )

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):

        cadre_cursor = self_client["Cadre"]
        data = cadre_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':exclamation: There is no data in the list!')

        apply_info = str()
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
            await ctx.author.send(apply_info)

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def permit(self, ctx, permit_id: int):

        cadre_cursor = self_client["Cadre"]
        data = cadre_cursor.find_one({"_id": permit_id})

        if not data:
            return await ctx.send(
                f':exclamation: There exists no applicant whose id is {permit_id}!'
            )

        await ctx.author.send(
            f':white_check_mark: You\'ve permitted user {data["name"]} to join cadre {data["apply_cadre"]}!'
        )

        member = await ctx.guild.fetch_member(data["_id"])
        await member.send(
            f':white_check_mark: 您於 {data["apply_time"]} 申請 {data["apply_cadre"]} 的程序已通過！\n'
            f'此為幹部群的連結，請在加入之後使用指令領取屬於你的身分組\n'
            f'{os.environ.get("Working_link")}'
        )

        cadre_cursor.delete_one({"_id": data["_id"]})

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def search(self, ctx, search_id: int):

        cadre_cursor = self_client["Cadre"]
        data = cadre_cursor.find_one({"_id": search_id})

        if not data:
            return await ctx.send(f':exclamation: There are no applicant whose Id is {search_id}!')

        await ctx.send(
            f'{data["name"]}({data["_id"]}): '
            f'{data["apply_cadre"]}, '
            f'{data["apply_time"]}'
        )

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remove(self, ctx, delete_id: int):

        cadre_cursor = self_client["Cadre"]
        data = cadre_cursor.find_one({"_id": delete_id})

        if not data:
            await ctx.send(f':exclamation: There exists no applicant whose id is {delete_id}!')

        cadre_cursor.delete_one({"_id": delete_id})
        await ctx.send(f'Member {data["name"]}({delete_id})\'s application has been removed!')


def setup(bot):
    bot.add_cog(Cadre(bot))
