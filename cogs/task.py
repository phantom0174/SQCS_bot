from core.setup import *
from functions import *
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
        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if now_time_info('date') == 1 and now_time_info('hour') >= 6 and quiz_data['event_status'] == 'False':
            await quiz_start(self.bot)
            await getChannel('_Report').send(f'[Auto]Quiz event start. {now_time_info("whole")}')
        elif now_time_info('date') == 7 and now_time_info('hour') >= 23 and quiz_data['event_status'] == 'True':
            await quiz_end(self.bot)
            await getChannel('_Report').send(f'[Auto]Quiz event end. {now_time_info("whole")}')

        if (1 <= now_time_info('date') <= 5) and quiz_data['event_status'] == 'True' and quiz_data[
            'stand_by_ans'] == 'N/A':
            member = await self.bot.fetch_user(610327503671656449)
            await member.send(':four_leaf_clover: My master, the correct answer hasn\'t been set yet!')

    @tasks.loop(minutes=10)
    async def db_backup(self):
        temp_file = open('jsons/dyn_setting.json', mode='r', encoding='utf8')
        dyn = json.load(temp_file)
        temp_file.close()

        if dyn['ldbh'] != now_time_info('hour'):
            file_name = 'db_backup/' + str(now_time_info('hour')) + '_backup.db'
            bck_db_conn = sqlite3.connect(file_name)
            await asyncio.sleep(10)
            sqlitebck.copy(connection, bck_db_conn)

            dyn['ldbh'] = now_time_info('hour')

            temp_file = open('jsons/dyn_setting.json', mode='w', encoding='utf8')
            json.dump(dyn, temp_file)
            temp_file.close()