from core.setup import jdata, client
import core.functions as func
from cogs.quiz import quiz_start, quiz_end
import discord
import asyncio
import json
import sys
import os
from discord.ext import commands, tasks
from core.classes import Cog_Extension
from pymongo import MongoClient


class Task(Cog_Extension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quiz_data_cursor = client["quiz_data"]

        self.quiz_auto.start()

    @tasks.loop(minutes=10)
    async def quiz_auto(self):
        await self.bot.wait_until_ready()

        quiz_status = self.quiz_data_cursor.find_one({"_id": 0})["event_status"]

        if func.now_time_info('date') == 1 and func.now_time_info('hour') >= 6 and quiz_status == 0:
            await quiz_start(self.bot)
            await func.getChannel(self.bot, '_Report').send(f'[Auto]Quiz event start. {func.now_time_info("whole")}')
        elif func.now_time_info('date') == 7 and func.now_time_info('hour') >= 23 and quiz_status == 1:
            await quiz_end(self.bot)
            await func.getChannel(self.bot, '_Report').send(f'[Auto]Quiz event end. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Task(bot))
