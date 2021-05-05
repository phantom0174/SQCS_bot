from core.db import self_client
from core.utils import Time
from cogs.sqcs_plugin.quiz import quiz_start, quiz_end
import discord
from discord.ext import tasks
from core.cog_config import CogExtension, JsonApi
from core.db import fluctlight_client


class Task(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quiz_set_cursor = self_client["QuizSetting"]

        self.quiz_auto.start()
        self.nt_auto.start()
        self.bot_activity.start()

    @tasks.loop(minutes=10)
    async def quiz_auto(self):
        await self.bot.wait_until_ready()

        report_channel = discord.utils.get(self.bot.guilds[1].text_channels, name='sqcs-report')

        quiz_status = self.quiz_set_cursor.find_one({"_id": 0})["event_status"]

        if Time.get_info('date') == 1 and Time.get_info('hour') >= 6 and not quiz_status:
            await quiz_start(self.bot)
            await report_channel.send(f'[AUTO QUIZ START][{Time.get_info("whole")}]')
        elif Time.get_info('date') == 7 and Time.get_info('hour') >= 23 and quiz_status:
            await quiz_end(self.bot)
            await report_channel.send(f'[AUTO QUIZ END][{Time.get_info("whole")}]')

    @tasks.loop(minutes=5)
    async def nt_auto(self):
        await self.bot.wait_until_ready()

        nt_list = JsonApi().get_json('NT')["id_list"]
        for member in self.bot.guilds[0].members:
            if member.id in nt_list:
                await member.send(':recycle:')
                await member.ban()

    @tasks.loop(minutes=10)
    async def bot_activity(self):
        await self.bot.wait_until_ready()

        fluctlight_cursor = fluctlight_client["MainFluctlights"]
        member_count = fluctlight_cursor.find({}).count()

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f'{member_count} 個活生生的搖光'
            )
        )


def setup(bot):
    bot.add_cog(Task(bot))
