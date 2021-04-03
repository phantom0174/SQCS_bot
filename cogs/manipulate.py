from discord.ext import commands
import core.functions as func
import time
from core.classes import Cog_Extension
from core.setup import jdata, client, fluctlight_client


class Manipulate(Cog_Extension):

    @commands.group()
    async def mani(self, ctx):
        pass

    @mani.command()
    @commands.has_any_role('總召', 'Administrator')
    async def uti_mani(self, ctx, attribute: str, target_id: int, delta_value: float):
        if attribute not in ['score', 'du', 'oca', 'sca', 'contrib', 'lvl_ind']:
            await ctx.send(f'There are no attribute {attribute}!')
            return

        fluctlight_cursor = fluctlight_client["light-cube-info"]
        data = fluctlight_cursor.find_one({"_id": target_id})

        if data.count() == 0:
            await ctx.send(f'There are no data of {target_id}!')
            return

        fluctlight_cursor.update_one({"_id": target_id}, {"$set": {attribute: delta_value}})

        data = fluctlight_cursor.find({"_id": target_id}, {attribute: 1})

        member_name = (await ctx.guild.fetch_user(target_id))
        await ctx.send(f'Member {member_name}\'s {attribute} has been set as {data[attribute]}!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group mani - uti_mani used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Manipulate(bot))
