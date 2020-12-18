from core.setup import connection, info, jdata
import functions as func
from cogs.quiz import quiz_start, quiz_end
import discord
import asyncio
import sqlitebck # can only use on console
import sqlite3
import json
import sys
import os
from discord.ext import commands, tasks
from core.classes import Cog_Extension

class Task(Cog_Extension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quiz_auto.start()
        self.db_backup.start()

    @tasks.loop(minutes=10)
    async def quiz_auto(self):
        await self.bot.wait_until_ready()

        with open('jsons/quiz.json', mode='r', encoding='utf8') as temp_file:
            quiz_data = json.load(temp_file)

        if func.now_time_info('date') == 1 and func.now_time_info('hour') >= 6 and quiz_data['event_status'] == 'False':
            await quiz_start(self.bot)
            await func.getChannel(self.bot, '_Report').send(f'[Auto]Quiz event start. {func.now_time_info("whole")}')
        elif func.now_time_info('date') == 7 and func.now_time_info('hour') >= 23 and quiz_data['event_status'] == 'True':
            await quiz_end(self.bot)
            await func.getChannel(self.bot, '_Report').send(f'[Auto]Quiz event end. {func.now_time_info("whole")}')

        if (1 <= func.now_time_info('date') <= 5) and quiz_data['event_status'] == 'True' and quiz_data[
            'stand_by_ans'] == 'N/A':
            member = await self.bot.fetch_user(610327503671656449)
            await member.send(':four_leaf_clover: My master, the correct answer hasn\'t been set yet!')

    @tasks.loop(minutes=10)
    async def db_backup(self):
        await self.bot.wait_until_ready()

        with open('jsons/dyn_setting.json', mode='r', encoding='utf8') as temp_file:
            dyn = json.load(temp_file)

        if dyn['ldbh'] != func.now_time_info('hour'):
            file_name = 'db_backup/' + str(func.now_time_info('hour')) + '_backup.db'
            bck_db_conn = sqlite3.connect(file_name)
            await asyncio.sleep(10)
            sqlitebck.copy(connection, bck_db_conn)

            dyn['ldbh'] = func.now_time_info('hour')

            with open('jsons/dyn_setting.json', mode='w', encoding='utf8') as temp_file:
                json.dump(dyn, temp_file)


def setup(bot):
    bot.add_cog(Task(bot))
