from discord.ext import commands
from core.classes import Cog_Extension
from core.setup import jdata, client, link, fluctlight_client
from pymongo import MongoClient


class Deep_Freeze(Cog_Extension):

    @commands.group()
    async def df(self, ctx):
        pass

    # deep freeze
    @df.command()
    @commands.has_any_role('總召', 'Administrator')
    async def mani(self, ctx, member_id: int, status: int):
        fluctlight_cursor = fluctlight_client["light-cube-info"]

        fluctlight_cursor.update_one({"_id": member_id}, {"$set": {"deep_freeze": status}})
        member = await self.bot.fetch_user(member_id)
        await member.send(f':exclamation: Your deep freeze status has been set to {status}')
        await ctx.send(':white_check_mark: Manipulation finished!')

    @df.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        await ctx.send(':hourglass_flowing_sand: Finding...')
        fluctlight_cursor = fluctlight_client["light-cube-info"]

        member_list = str()
        data = fluctlight_cursor.find({"deep_freeze": {"$eq": 1}})
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
