from core.db import self_client, fluctlight_client, JsonApi
from core.utils import Time
from cogs.sqcs_plugin.quiz import quiz_start, quiz_end
import discord
from discord.ext import tasks
from core.cog_config import CogExtension
from core.fluctlight_ext import Fluct


class Task(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quiz_set_cursor = self_client["QuizSetting"]

        self.quiz_auto.start()
        self.role_update_check.start()
        self.local_log_upload.start()

    @tasks.loop(minutes=50)
    async def quiz_auto(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(784607509629239316)
        report_channel = discord.utils.get(guild.text_channels, name='sqcs-report')

        quiz_status = self.quiz_set_cursor.find_one({"_id": 0})["event_status"]

        def quiz_ready_to_start():
            return Time.get_info('date') == 1 and Time.get_info('hour') >= 6 and not quiz_status

        def quiz_ready_to_end():
            return Time.get_info('date') == 7 and Time.get_info('hour') >= 22 and quiz_status

        if quiz_ready_to_start():
            await quiz_start(self.bot)
            await report_channel.send(f'[AUTO QUIZ START][{Time.get_info("whole")}]')
        elif quiz_ready_to_end():
            await quiz_end(self.bot)
            await report_channel.send(f'[AUTO QUIZ END][{Time.get_info("whole")}]')

    @tasks.loop(hours=2)
    async def role_update_check(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(743507979369709639)
        auto_role = guild.get_role(823804080199565342)
        neutral_role = guild.get_role(823803958052257813)
        fluctlight_cursor = fluctlight_client["MainFluctlights"]

        for member in guild.members:
            if member.bot:
                continue

            if neutral_role in member.roles:
                member_active_data = fluctlight_cursor.find_one({"_id": member.id})
                if member_active_data is None:
                    await Fluct().reset_main(member.id, guild)
                    continue

                quiz_crt_count = member_active_data["quiz_correct_count"]
                lect_attend_count = member_active_data["lect_attend_count"]

                if quiz_crt_count >= 2 and lect_attend_count >= 4:
                    await member.remove_roles(neutral_role)
                    await member.add_roles(auto_role)
                    await member.send(':partying_face: 恭喜！你已升級為自由量子！')

    @tasks.loop(minutes=30)
    async def local_log_upload(self):
        with open('./bot.log', mode='r', encoding='utf8') as temp_file:
            local_logs = temp_file.read().split('\n')

        if local_logs is None:
            return

        while str('') in local_logs:
            local_logs.remove('')

        # upload logs
        log_json = JsonApi().get('CmdLogging')
        for log in local_logs:
            log_json['logs'].append(log)
        JsonApi().put('CmdLogging', log_json)

        # flush local logs
        with open('./bot.log', mode='w', encoding='utf8') as temp_file:
            temp_file.write('')


def setup(bot):
    bot.add_cog(Task(bot))
