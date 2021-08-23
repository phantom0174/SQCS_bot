from discord.ext import commands
import asyncio
import time
from ...core.db.jsonstorage import JsonApi
from ...core.utils import Time
from ...core.cog_config import CogExtension
from ...core.fluctlight_ext import Fluct


class React(CogExtension):

    @commands.Cog.listener()
    async def on_member_join(self, member):
        nts = JsonApi.get('NT')["id_list"]
        if member.id in nts:
            return await member.ban()

        if member.bot or member.guild.id != 743507979369709639:
            return

        default_role = member.guild.get_role(823803958052257813)
        await member.add_roles(default_role)

        time_status = Time.get_range(Time.get_info('hour'))

        msg = await JsonApi.get_humanity(f'join/opening/{time_status}', '\n')
        msg += await JsonApi.get_humanity('join/opening/main')
        try:
            await member.send(msg)
        except BaseException:
            pass
        await asyncio.sleep(30)

        msg = await JsonApi.get_humanity('join/hackmd_read')
        try:
            reaction_msg = await member.send(msg)
        except BaseException:
            pass
        await reaction_msg.add_reaction('⭕')
        await reaction_msg.add_reaction('❌')

        def check(check_reaction, check_user):
            return check_reaction.message.id == reaction_msg.id and check_user.id == member.id

        deep_freeze_status = bool()
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)

            if reaction.emoji == '⭕':
                msg = await JsonApi.get_humanity('join/df_1', '\n')
                deep_freeze_status = True
            elif reaction.emoji == '❌':
                msg = await JsonApi.get_humanity('join/df_0', '\n')
                deep_freeze_status = False
        except asyncio.TimeoutError:
            msg = await JsonApi.get_humanity('join/time_out', '\n')
            deep_freeze_status = False

        msg += await JsonApi.get_humanity('join/contact_method')

        try:
            await member.send(msg)
        except BaseException:
            pass

        # create personal fluctlight data
        start_time = time.time()
        fluct_ext = Fluct()
        await fluct_ext.create_main(member.guild, deep_freeze_status, member.id)
        await fluct_ext.create_vice(member.id)
        end_time = time.time()

        msg = await JsonApi.get_humanity('join/fl_create_finish')
        try:
            await member.send(msg)
            time_duration = round(end_time - start_time, 2)
            await member.send(f'順帶一提，我用了 {time_duration} (sec) 建立你的檔案><!')
        except BaseException:
            pass


def setup(bot):
    bot.add_cog(React(bot))
