from discord.ext import commands
import asyncio
import time
from core.db import huma_get, fluctlight_client, JsonApi
from core.utils import Time
from core.cog_config import CogExtension


class React(CogExtension):

    @commands.Cog.listener()
    async def on_member_join(self, member):
        nts = JsonApi().get('NT')["id_list"]
        if member.id in nts:
            return await member.ban()

        if member.bot or member.guild.id != 743507979369709639:
            return

        default_role = member.guild.get_role(823803958052257813)
        await member.add_roles(default_role)

        time_status = Time.get_range(Time.get_info('hour'))

        msg = await huma_get(f'join/opening/{time_status}', '\n')
        msg += await huma_get('join/opening/main')
        await member.send(msg)
        await asyncio.sleep(30)

        msg = await huma_get('join/hackmd_read')
        reaction_msg = await member.send(msg)
        await reaction_msg.add_reaction('⭕')
        await reaction_msg.add_reaction('❌')

        def check(check_reaction, check_user):
            return check_reaction.message.id == reaction_msg.id and check_user.id == member.id

        deep_freeze_status = bool()
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)

            if reaction.emoji == '⭕':
                msg = await huma_get('join/df_1', '\n')
                deep_freeze_status = True
            elif reaction.emoji == '❌':
                msg = await huma_get('join/df_0', '\n')
                deep_freeze_status = False
        except asyncio.TimeoutError:
            msg = await huma_get('join/time_out', '\n')
            deep_freeze_status = False

        msg += await huma_get('join/contact_method')

        await member.send(msg)

        # create personal fluctlight data
        start_time = time.time()

        main_fluct_cursor = fluctlight_client["MainFluctlights"]
        vice_fluct_cursor = fluctlight_client["ViceFluctlights"]

        default_main_fluctlight = {
            "_id": member.id,
            "name": member.display_name,
            "score": 0,
            "week_active": False,
            "contrib": 0,
            "lvl_ind": 0,
            "deep_freeze": deep_freeze_status,
            "log": '',
            "lect_attend_count": 0,
            "quiz_submit_count": 0,
            "quiz_correct_count": 0
        }
        try:
            main_fluct_cursor.insert_one(default_main_fluctlight)
        except:
            pass

        default_vice_fluctlight = {
            "_id": member.id,
            "du": 0,
            "mdu": 0,
            "oc_auth": 0,
            "sc_auth": 0,
        }
        try:
            vice_fluct_cursor.insert_one(default_vice_fluctlight)
        except:
            pass

        end_time = time.time()

        msg = await huma_get('join/fl_create_finish')
        await member.send(msg)
        time_duration = round(end_time - start_time, 2)
        await member.send(f'順帶一提，我用了 {time_duration} (sec) 建立你的檔案><!')


def setup(bot):
    bot.add_cog(React(bot))
