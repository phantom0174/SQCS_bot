from discord.ext import commands
from core.cog_config import CogExtension
from core.db import fluctlight_client, self_client, huma_get
from core.fluctlight_ext import Fluct


class PersonalInfo(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def fluct(self, ctx):
        pass

    @fluct.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remedy(self, ctx, members_id: commands.Greedy[int], delta_value: float):
        fl_cursor = fluctlight_client["MainFluctlights"]
        score_set_cursor = self_client["ScoreSetting"]
        score_weight = score_set_cursor.find_one({"_id": 0})["score_weight"]

        for member_id in members_id:
            try:
                execute = {
                    "$inc": {
                        "score": round(delta_value * score_weight, 2)
                    }
                }
                fl_cursor.update_one({"_id": member_id}, execute)
                await Fluct().active_log_update(member_id)

                member = await ctx.guild.fetch_member(member_id)
                msg = f'耶！你被管理員加了 {delta_value} 分！' + '\n'
                msg += huma_get('main/remedy/pt_1')
                await member.send(msg)
            except:
                await ctx.send(f':x: 彌補 {member_id} 時發生了錯誤！彌補分數：{delta_value}')

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @fluct.command()
    async def delete(self, ctx, member_id: int):
        cursors = [
            fluctlight_client["MainFluctlights"],
            fluctlight_client["ViceFluctlights"]
        ]

        for cursor in cursors:
            try:
                cursor.delete_one({"_id": member_id})
            except:
                await ctx.send(f':x: 操作指標 {cursor} 時發生了錯誤！')

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @fluct.command()
    async def reset(self, ctx, member_id: int):
        await Fluct().reset_main(member_id, ctx.guild)
        await Fluct().reset_vice(member_id)

        await ctx.send(':white_check_mark: 指令執行完畢！')


def setup(bot):
    bot.add_cog(PersonalInfo(bot))
