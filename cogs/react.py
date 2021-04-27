from discord.ext import commands
import asyncio
import time
from core.setup import rsp, fluctlight_client
import core.functions as func
from core.classes import CogExtension, JsonApi


class React(CogExtension):

    @commands.Cog.listener()
    async def on_member_join(self, member):
        nts = JsonApi().get_json('NT')["id_list"]
        if (member.id in nts) or member.bot:
            return

        time_status = await func.get_time_title(func.now_time_info('hour'))

        msg = '\n'.join(rsp["join"]["opening"][time_status]) + '\n'
        msg += '\n'.join(rsp["join"]["opening"]["main"])
        await member.send(msg)
        await asyncio.sleep(60)

        msg = '\n'.join(rsp["join"]["hackmd_read"])
        reaction_msg = await member.send(msg)
        await reaction_msg.add_reaction('⭕')
        await reaction_msg.add_reaction('❌')

        def check(reaction, user):
            return reaction.message.id == reaction_msg.id and user.id == member.id

        deep_freeze_status = bool()
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)

            if reaction.emoji == '⭕':
                msg = '\n'.join(rsp["join"]["df_1"])
                deep_freeze_status = True
            elif reaction.emoji == '❌':
                msg = '\n'.join(rsp["join"]["df_0"])
                deep_freeze_status = False

            # remember to delete the invalid_syntax part of humanity ext.
            # else:
            #     msg = '\n'.join(rsp["join"]["invalid_syntax"])
            #     deep_freeze_status = False
        except asyncio.TimeoutError:
            msg = '\n'.join(rsp["join"]["time_out"])
            deep_freeze_status = False

        # another \n for last un-inserted \n
        msg += '\n' + '\n'.join(rsp["join"]["contact_method"])

        await member.send(msg)

        # create personal fluctlight data
        start_time = time.time()

        main_fluct_cursor = fluctlight_client["MainFluctlights"]
        vice_fluct_cursor = fluctlight_client["ViceFluctlights"]
        act_cursor = fluctlight_client["active-logs"]

        default_main_fluctlight = {
            "_id": member.id,
            "name": member.display_name,
            "score": 0,
            "week_active": False,
            "contrib": 0,
            "lvl_ind": 0,
            "deep_freeze": deep_freeze_status
        }
        default_vice_fluctlight = {
            "_id": member.id,
            "du": 0,
            "mdu": 0,
            "oc_auth": 0,
            "sc_auth": 0,
        }
        default_act = {
            "_id": member.id,
            "log": ''
        }

        try:
            main_fluct_cursor.insert_one(default_main_fluctlight)
        except:
            pass

        try:
            vice_fluct_cursor.insert_one(default_vice_fluctlight)
        except:
            pass

        try:
            act_cursor.insert_one(default_act)
        except:
            pass

        end_time = time.time()

        msg = '\n'.join(rsp["join"]["fl_create_finish"])
        await member.send(msg)
        await member.send(f'順帶一提，我用了 {round(end_time - start_time, 2)} (sec) 建立你的檔案><!')


def setup(bot):
    bot.add_cog(React(bot))
