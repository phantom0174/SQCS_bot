from core.classes import Cog_Extension, JsonApi
from discord.ext import commands
import core.functions as func
import time
from core.setup import rsp, fluctlight_client
import asyncio


class React(Cog_Extension):

    @commands.Cog.listener()
    async def on_member_join(self, member):
        nts = JsonApi().get_json('NT')["id_list"]
        if member.id in nts:
            return

        if member.bot:
            return

        time_status = await func.get_time_title(func.now_time_info('hour'))

        msg = '\n'.join(rsp["join"]["opening"][time_status]) + '\n'
        msg += '\n'.join(rsp["join"]["opening"]["main"])
        await member.send(msg)
        await asyncio.sleep(60)

        msg = '\n'.join(rsp["join"]["hackmd_read"])
        await member.send(msg)

        def check(message):
            return message.channel == member.dm_channel and message.author == member

        try:
            deep_freeze_status = (await self.bot.wait_for('message', check=check, timeout=60.0)).content

            if deep_freeze_status == 'y':
                msg = '\n'.join(rsp["join"]["df_1"])
                deep_freeze_status = 1
            elif deep_freeze_status == 'n':
                msg = '\n'.join(rsp["join"]["df_0"])
                deep_freeze_status = 0
            else:
                msg = '\n'.join(rsp["join"]["invalid_syntax"])
                deep_freeze_status = 0
        except asyncio.TimeoutError:
            msg = '\n'.join(rsp["join"]["time_out"])
            deep_freeze_status = 0

        # another \n for last un-inserted \n
        msg += '\n' + '\n'.join(rsp["join"]["contact_method"])

        await member.send(msg)

        # create personal fluctlight data
        start_time = time.time()

        fluctlight_cursor = fluctlight_client["light-cube-info"]

        member_fluctlight = {
            "_id": member.id,
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
            "deep_freeze": deep_freeze_status
        }

        try:
            fluctlight_cursor.insert_one(member_fluctlight)
        except:
            fluctlight_cursor.delete_one({"_id": member.id})
            fluctlight_cursor.insert_one(member_fluctlight)

        end_time = time.time()

        msg = '\n'.join(rsp["join"]["fl_create_finish"])
        await member.send(msg)
        await member.send(f'順帶一提，我用了 {round(end_time - start_time, 2)} (sec) 建立你的檔案><!')


def setup(bot):
    bot.add_cog(React(bot))
