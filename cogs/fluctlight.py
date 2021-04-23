from discord.ext import commands
from core.classes import CogExtension
from core.setup import fluctlight_client
import core.functions as func


class PersonalInfo(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def fluct(self, ctx):
        pass

    @fluct.command()
    async def delete(self, ctx, member_id: int):
        cursors = [
            fluctlight_client["MainFluctlights"],
            fluctlight_client["ViceFluctlights"],
            fluctlight_client["ActiveLogs"]
        ]

        for cursor in cursors:
            try:
                cursor.delete_one({"_id": member_id})
            except:
                await ctx.send(f':exclamation: Error when manipulating cursor {cursor}')

        await ctx.send(':white_check_mark: Operation finished!')

    @fluct.command()
    async def reset(self, ctx, member_id: int):
        main_fluct_cursor = fluctlight_client["MainFluctlights"]
        vice_fluct_cursor = fluctlight_client["ViceFluctlights"]
        act_cursor = fluctlight_client["active-logs"]

        default_main_fluctlight = {
            "_id": member_id,
            "name": await func.get_member_nick_name(ctx.guild, member_id),
            "score": 0,
            "week_active": False,
            "contrib": 0,
            "lvl_ind": 0,
            "deep_freeze": False
        }
        default_vice_fluctlight = {
            "_id": member_id,
            "du": 0,
            "mdu": 0,
            "oc_auth": 0,
            "sc_auth": 0,
        }
        default_act = {
            "_id": member_id,
            "log": ''
        }

        try:
            main_fluct_cursor.delete_one({"_id": member_id})
            main_fluct_cursor.insert_one(default_main_fluctlight)
        except:
            await ctx.send(':exclamation: Error when manipulating collection MainFluctlights')

        try:
            vice_fluct_cursor.delete_one({"_id": member_id})
            vice_fluct_cursor.insert_one(default_vice_fluctlight)
        except:
            await ctx.send(':exclamation: Error when manipulating collection ViceFluctlights')

        try:
            act_cursor.delete_one({"_id": member_id})
            act_cursor.insert_one(default_act)
        except:
            await ctx.send(':exclamation: Error when manipulating collection ActiveLogs')

        await ctx.send(':white_check_mark: Operation finished!')


def setup(bot):
    bot.add_cog(PersonalInfo(bot))
