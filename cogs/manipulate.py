from discord.ext import commands
from core.classes import Cog_Extension
from core.setup import client, fluctlight_client


class Manipulate(Cog_Extension):

    @commands.group()
    async def mani(self, ctx):
        pass

    @mani.command()
    @commands.has_any_role('總召', 'Administrator')
    async def uti_mani(self, ctx, attribute: str, target_id: int, delta_value: float):

        if attribute not in ['score', 'du', 'oca', 'sca', 'contrib', 'lvl_ind']:
            await ctx.send(f':exclamation: There exists no attribute {attribute}!')
            return

        fluctlight_cursor = fluctlight_client["light-cube-info"]
        data = fluctlight_cursor.find_one({"_id": target_id})

        if not data:
            await ctx.send(f':exclamation: There are no data of {target_id}!')
            return

        execute = {
            "$set": {
                attribute: delta_value
            }
        }
        fluctlight_cursor.update_one({"_id": target_id}, execute)

        data = fluctlight_cursor.find({"_id": target_id}, {attribute: 1})

        member_name = (await ctx.guild.fetch_user(target_id))
        await ctx.send(f'Member {member_name}\'s {attribute} has been set as {data[attribute]}!')

    @mani.command()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz(self, ctx, member_id: int, alter: int):

        quiz_cursor = client["quiz"]
        execute = {
            "$set": {
                "correct": alter
            }
        }
        quiz_cursor.update_one({"_id": member_id}, execute)

        member_name = (await self.bot.fetch_user(member_id)).name
        await ctx.send(f'Member {member_name}\'s correct answer has been set as {alter}!')


def setup(bot):
    bot.add_cog(Manipulate(bot))
