from discord.ext import commands
from core.classes import CogExtension, Fluct
from core.setup import fluctlight_client, client, rsp
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
        await Fluct(member_id).reset_main(member_id, ctx.guild)
        await Fluct(member_id).reset_vice(member_id)
        await Fluct(member_id).reset_active(member_id)

        await ctx.send(':white_check_mark: Operation finished!')


def setup(bot):
    bot.add_cog(PersonalInfo(bot))
