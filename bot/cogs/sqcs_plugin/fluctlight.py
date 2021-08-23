from discord.ext import commands, tasks
from ...core.cog_config import CogExtension
from ...core.db.jsonstorage import JsonApi
from ...core.db.mongodb import Mongo
from ...core.fluctlight_ext import Fluct


class Fluctlight(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def fluct(self, ctx):
        pass

    @fluct.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remedy(self, ctx, delta_value: float, members_id: commands.Greedy[int]):
        fluct_ext = Fluct(score_mode='custom')
        for member_id in members_id:
            try:
                final_delta_score = await fluct_ext.add_score(member_id, delta_value)
                await fluct_ext.active_log_update(member_id)

                member = ctx.guild.get_member(member_id)
                msg = f'耶！你被加了 {final_delta_score} 分！' + '\n'
                msg += await JsonApi.get_humanity('main/remedy/pt_1')

                try:
                    await member.send(msg)
                except BaseException:
                    pass
            except BaseException:
                await ctx.send(f':x: 彌補 {member_id} 時發生了錯誤！彌補分數：{delta_value}')

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @fluct.command()
    async def create(self, ctx, member_id: int):
        """cmd
        幫 成員<member_id> 手動產生搖光。

        .member_id: 成員在Discord中的id
        """
        fluct_ext = Fluct()
        await fluct_ext.create_main(ctx.guild, False, member_id)
        await fluct_ext.create_vice(member_id)

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @fluct.command()
    async def delete(self, ctx, member_id: int):
        """cmd
        幫 成員<member_id> 手動刪除搖光。

        .member_id: 成員在Discord中的id
        """
        fluct_ext = Fluct()
        await fluct_ext.delete_main(member_id)
        await fluct_ext.delete_vice(member_id)

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @fluct.command()
    async def reset(self, ctx, member_id: int):
        """cmd
        幫 成員<member_id> 手動重新設定搖光。

        .member_id: 成員在Discord中的id
        """
        fluct_ext = Fluct()
        await fluct_ext.reset_main(ctx.guild, False, member_id)
        await fluct_ext.reset_vice(member_id)

        await ctx.send(':white_check_mark: 指令執行完畢！')


class FluctlightAuto(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_missing_member_fluctlight.start()
        self.delete_unused_fluctlight.start()

    @tasks.loop(hours=3)
    async def create_missing_member_fluctlight(self):
        await self.bot.wait_until_ready()

        main_cursor, vice_cursor = Mongo('LightCube').get_curs(['MainFluctlights', 'ViceFluctlights'])

        guild = self.bot.get_guild(743507979369709639)

        fluct_ext = Fluct()
        for member in guild.members:
            if member.bot:
                continue

            member_main_fluct = main_cursor.find_one({"_id": member.id})
            member_vice_fluct = vice_cursor.find_one({"_id": member.id})

            if not member_main_fluct:
                await fluct_ext.create_main(guild, False, member.id)

            if not member_vice_fluct:
                await fluct_ext.create_vice(member.id)

    @tasks.loop(hours=12)
    async def delete_unused_fluctlight(self):
        await self.bot.wait_until_ready()

        main_cursor, vice_cursor = Mongo('LightCube').get_curs(['MainFluctlights', 'ViceFluctlights'])

        main_data = main_cursor.find({})
        vice_data = vice_cursor.find({})

        guild = self.bot.get_guild(743507979369709639)

        fluct_ext = Fluct()
        for member_data in main_data:
            member = guild.get_member(member_data['_id'])

            if member is None or member.bot:
                await fluct_ext.delete_main(member_data['_id'])

        for member_data in vice_data:
            member = guild.get_member(member_data['_id'])

            if member is None or member.bot:
                await fluct_ext.delete_vice(member_data['_id'])


def setup(bot):
    bot.add_cog(Fluctlight(bot))
    bot.add_cog(FluctlightAuto(bot))
