from discord.ext import commands
import time
from core.classes import CogExtension
from core.setup import client, fluctlight_client


class PersonalInfo(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def fluct(self, ctx):
        pass

    @fluct.command()
    async def delete(self, ctx, member_id: int):
        fluct_cursor = fluctlight_client["light-cube-info"]
        active_log_cursor = fluctlight_client["active-logs"]

        try:
            fluct_cursor.delete_one({"_id": member_id})
            active_log_cursor.delete_one({"_id": member_id})
            await ctx.send(':white_check_mark: Successfully deleted!')
            return
        except:
            await ctx.send(':exclamation: Operation failed')
            return

    @fluct.command()
    async def reset(self, ctx, member_id: int):
        fluct_cursor = fluctlight_client["light-cube-info"]
        active_log_cursor = fluctlight_client["active-logs"]

        default_fluctlight = {
            "_id": member_id,
            "score": 0,
            "du": 0,
            "oc_auth": 0,
            "sc_auth": 0,
            "lvl_ind": 0,
            "mdu": 0,
            "odu": 0,
            "odu_time": time.time(),
            "contrib": 0,
            "week_active": 0,
            "deep_freeze": 0
        }
        default_log = {
            "_id": member_id,
            "log": ''
        }

        try:
            fluct_cursor.delete_one({"_id": member_id})
            fluct_cursor.insert_one(default_fluctlight)
            active_log_cursor.delete_one({"_id": member_id})
            active_log_cursor.insert_one(default_log)
            await ctx.send(':white_check_mark: Operation finished!')
            return
        except:
            await ctx.send(':exclamation: Operation failed')
            return


def setup(bot):
    bot.add_cog(PersonalInfo(bot))
