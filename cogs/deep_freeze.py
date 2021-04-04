from discord.ext import commands
from core.classes import Cog_Extension
from core.setup import fluctlight_client
import core.functions as func


class Deep_Freeze(Cog_Extension):

    @commands.group()
    async def df(self, ctx):
        pass

    @df.command()
    @commands.has_any_role('總召', 'Administrator')
    async def mani(self, ctx, member_id: int, status: int):
        await func.report(self.bot, f'[CMD EXECUTED][df][mani][{ctx.author.name}][{ctx.author.id}]\n'
                                    f'[member_id: {member_id}, status: {status}]')

        fluctlight_cursor = fluctlight_client["light-cube-info"]

        try:
            fluctlight_cursor.update_one({"_id": member_id}, {"$set": {"deep_freeze": status}})
            member = await ctx.guild.fetch_member(member_id)

            await member.send(f':exclamation: 你的 `deep freeze` 狀態被設定為 {status} 了！')
            await ctx.send(':white_check_mark: Manipulation finished!')
        except Exception as e:
            await ctx.send(content=e, delete_after=5.0)
            return

    @df.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        await func.report(self.bot, f'[CMD EXECUTED][df][list][{ctx.author.name}][{ctx.author.id}]')

        await ctx.send(':hourglass_flowing_sand: Finding...')
        fluctlight_cursor = fluctlight_client["light-cube-info"]
        data = fluctlight_cursor.find({"deep_freeze": {"$eq": 1}})

        if data.count() == 0:
            await ctx.send(':exclamation: There are no member in deep_freeze status!')
            return

        member_list = str()
        for member in data:
            member_name = (await ctx.guild.fetch_member(member["_id"])).nick
            if member_name is None:
                member_name = (await ctx.guild.fetch_member(member["_id"])).name

            member_list += member_name + '\n'

            if len(member_list) > 1600:
                await ctx.send(member_list)
                member_list = ''

        if len(member_list) > 0:
            await ctx.send(member_list)

        await ctx.send(':white_check_mark: Logging finished!')


def setup(bot):
    bot.add_cog(Deep_Freeze(bot))
