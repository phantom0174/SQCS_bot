from discord.ext import commands
from core.classes import CogExtension
from core.setup import fluctlight_client, client, rsp
import core.functions as func
import core.score_module as sm


class PersonalInfo(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def fluct(self, ctx):
        pass

    @fluct.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remedy(self, ctx, member_id: int, delta_value: float):
        fl_cursor = fluctlight_client["MainFluctlights"]
        score_set_cursor = client["ScoreSetting"]
        score_weight = score_set_cursor.find_one({"_id": 0})["score_weight"]

        try:
            execute = {
                "$inc": {
                    "score": round(delta_value * score_weight, 2)
                }
            }
            fl_cursor.update_one({"_id": member_id}, execute)
            await sm.active_log_update(member_id)

            member = await ctx.guild.fetch_member(member_id)
            msg = f'耶！你被管理員加了 {delta_value} 分！' + '\n'
            msg += rsp["main"]["mibu"]["pt_1"]
            await member.send(msg)
        except:
            await ctx.send(f':exclamation: Error when remedying {member_id}, value: {delta_value}!')

        await ctx.send(':white_check_mark: Operation finished!')

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
