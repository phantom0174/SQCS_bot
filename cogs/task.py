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


class Task(Cog_Extension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.quiz_auto.start()
        self.nick_auto.start()

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

    @tasks.loop(hours=6)
    async def nick_auto(self):
        await self.bot.wait_until_ready()

        if 6 <= func.now_time_info('hour') <= 18:
            members = self.bot.guilds[0].members

            for member in members:
                if member.nick is None:
                    await member.send('為讓伺服器正常運作，請趕快設定暱稱！')


def setup(bot):
    bot.add_cog(Task(bot))
