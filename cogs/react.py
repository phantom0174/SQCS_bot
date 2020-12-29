from core.classes import Cog_Extension
from discord.ext import commands
import core.functions as func
import json
import time
from pymongo import MongoClient
from core.setup import client, link
import asyncio


class React(Cog_Extension):

    @commands.command()
    async def msg_re(self, ctx, *, msg):
        re_msg = msg.split('\n')
        for log in re_msg:
            await ctx.send(log)

        await func.getChannel(self.bot, '_Report').send(f'[Command]msg_re used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        with open('./jsons/join_messages.json', mode='r', encoding='utf8') as temp_file:
            msg_json = json.load(temp_file)

        msg = '\n'.join(msg_json["join_opening"])
        await member.send(msg)
        await asyncio.sleep(60)

        msg = '\n'.join(msg_json["hackmd_read"])
        await member.send(msg)

        def check(message):
            return message.channel == member.dm_channel and message.author == member

        try:
            deep_freeze_status = (await self.bot.wait_for('message', check=check, timeout=60.0)).content

            if deep_freeze_status == 'y':
                msg = '\n'.join(msg_json["df_1"])
                deep_freeze_status = 1
            elif deep_freeze_status == 'n':
                msg = '\n'.join(msg_json["df_0"])
                deep_freeze_status = 0
            else:
                msg = '\n'.join(msg_json["invalid_syntax"])
                deep_freeze_status = 0
        except asyncio.TimeoutError:
            msg = '\n'.join(msg_json["time_out"])
            deep_freeze_status = 0

        msg += '\n'.join(msg_json["contact_method"])

        await member.send(msg)

        # create personal fluctlight data
        fluctlight_client = MongoClient(link)["LightCube"]
        fluctlight_cursor = fluctlight_client["light-cube-info"]

        member_fluctlight = {"_id": member.id,
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
                             "deep_freeze": deep_freeze_status}

        try:
            fluctlight_cursor.insert_one(member_fluctlight)
        except:
            fluctlight_cursor.delete_one({"_id": member.id})
            fluctlight_cursor.insert_one(member_fluctlight)

        msg = '\n'.join(msg_json["fl_create_finish"])
        await member.send(msg)


def setup(bot):
    bot.add_cog(React(bot))
