from discord.ext import tasks
from ..core.cog_config import CogExtension
from ..core.fluctlight_ext import Fluct
from ..core.db.mongodb import Mongo


class Task(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.role_update_check.start()

    @tasks.loop(hours=2)
    async def role_update_check(self):
        await self.bot.wait_until_ready()

        guild = self.bot.get_guild(743507979369709639)
        auto_role = guild.get_role(823804080199565342)
        neutral_role = guild.get_role(823803958052257813)
        fluctlight_cursor = Mongo('LightCube').get_cur('MainFluctlights')

        fluct_ext = Fluct()
        for member in guild.members:
            if member.bot:
                continue

            if neutral_role in member.roles:
                member_active_data = fluctlight_cursor.find_one({"_id": member.id})
                if member_active_data is None:
                    await fluct_ext.create_main(guild, False, member.id)
                    continue

                quiz_crt_count = member_active_data["quiz_correct_count"]
                lect_attend_count = member_active_data["lect_attend_count"]

                if quiz_crt_count >= 2 and lect_attend_count >= 4:
                    await member.remove_roles(neutral_role)
                    await member.add_roles(auto_role)

                    # no perm to send msg to user via server
                    try:
                        await member.send(':partying_face: 恭喜！你已升級為自由量子！')
                    except BaseException:
                        pass


def setup(bot):
    bot.add_cog(Task(bot))
