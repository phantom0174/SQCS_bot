from discord.ext import commands
from core.classes import CogExtension
from core.setup import fluctlight_client
import core.functions as func


class DeepFreeze(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def df(self, ctx):
        pass

    @df.command()
    async def mani(self, ctx, member_id: int, status: int):

        if status not in [0, 1]:
            return await ctx.send(':exclamation: Status must be either 0 or 1')

        fluct_cursor = fluctlight_client["MainFluctlights"]
        try:
            execute = {
                "$set": {
                    "deep_freeze": bool(status)
                }
            }
            fluct_cursor.update_one({"_id": member_id}, execute)
            member = await ctx.guild.fetch_member(member_id)

            await member.send(f':exclamation: 你的 `deep freeze` 狀態被設定為 {bool(status)} 了！')
            await ctx.send(':white_check_mark: Manipulation finished!')
        except Exception as e:
            return await ctx.send(content=e, delete_after=5.0)

    @df.command()
    async def list(self, ctx):
        await ctx.send(':hourglass_flowing_sand: Finding...')

        fluct_cursor = fluctlight_client["MainFluctlights"]
        data = fluct_cursor.find({"deep_freeze": {"$eq": True}})

        if data.count() == 0:
            return await ctx.send(':exclamation: There are no member in deep_freeze status!')

        member_list = str()
        for member in data:
            member_name = await func.get_member_nick_name(ctx.guild, member["_id"])

            member_list += member_name + '\n'

            if len(member_list) > 1600:
                await ctx.send(member_list)
                member_list = ''

        if len(member_list) > 0:
            await ctx.send(member_list)

        await ctx.send(':white_check_mark: Logging finished!')


def setup(bot):
    bot.add_cog(DeepFreeze(bot))
