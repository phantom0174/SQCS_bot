from core.classes import Cog_Extension
from core.setup import jdata, client
from discord.ext import commands
import core.functions as func


class Cadre(Cog_Extension):

    @commands.group()
    async def ca(self, ctx):
        pass

    @ca.command()
    async def apply(self, ctx, cadre):
        if ctx.channel.id != 774794670034124850:
            return

        applicant = ctx.author.id
        if func.cadre_trans(cadre) == -1:
            await ctx.send(f':exclamation: There are no cadre called {cadre}!')
            return

        cadre_cursor = client["cadre"]
        data = cadre_cursor.find_one({"_id": applicant})

        if data is not None:
            await ctx.author.send(f':exclamation: You\'ve already made a application!\n'
                                  f'Id: {data["_id"]}, Apply Cadre: {data["apply_cadre"]}, Apply Time: {data["apply_time"]}')
            return

        apply_time = func.now_time_info('whole')
        apply_info = {"_id": applicant, "apply_cadre": cadre, "apply_time": apply_time}
        cadre_cursor.insert_one(apply_info)

        await ctx.send(f':white_check_mark: Application committed!\n'
                       f'Id: {applicant}, Apply Cadre: {cadre}, Apply Time: {apply_time}')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group ca - apply used by member {applicant}. {func.now_time_info("whole")}')

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):

        cadre_cursor = client["cadre"]
        data = cadre_cursor.find({})

        apply_info = str()
        for item in data:
            member_name = await self.bot.guilds[0].fetch_member(item["_id"])
            if member_name is None:
                member_name = await self.bot.fetch_user(item["_id"])

            apply_info += f'{member_name}({item["_id"]}): {item["apply_cadre"]}, {item["apply_time"]}\n'

        if len(apply_info) == 0:
            apply_info = ':exclamation: There are no application!'

        await ctx.author.send(apply_info)

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group ca - list used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def permit(self, ctx, permit_id: int):

        cadre_cursor = client["cadre"]
        data = cadre_cursor.find_one({"_id": permit_id})

        if data.count() == 0:
            await ctx.send(f':exclamation: There are no applicant whose id is {permit_id}!')
            return

        member = await ctx.guild.fetch_member(data["_id"])

        await ctx.author.send(
            f':white_check_mark: You\'ve permitted user {member.name} to join cadre {data["apply_cadre"]}!\n'
            f'此為幹部群的連結，請在加入之後使用指令領取屬於你的身分組')
        await member.send(f':white_check_mark: You\'ve been permitted to join cadre {data["apply_cadre"]}!')

        cadre_cursor.delete_one({"_id": data["_id"]})

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group ca - permit used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @ca.command()
    @commands.has_any_role('總召', 'Administrator')
    async def search(self, ctx, search_id: int):

        cadre_cursor = client["cadre"]
        data = cadre_cursor.find_one({"_id": search_id})

        if data.count() == 0:
            await ctx.send(f':exclamation: There are no applicant whose Id is {search_id}!')
            return

        member = await ctx.guild.fetch_member(data["_id"])
        await ctx.send(f'{member.name}: {data["apply_cadre"]}, {data["apply_time"]}')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group ca - search used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @ca.command()
    async def remove(self, ctx, delete_id: int):
        cadre_cursor = client["cadre"]
        data = cadre_cursor.find_one({"_id": delete_id})

        if data.count() == 0:
            await ctx.send(f':exclamation: There are no applicant whose Id is {delete_id}!')

        member_name = await self.bot.guilds[0].fetch_member(data["_id"])
        if member_name is None:
            member_name = await self.bot.fetch_user(data["_id"])

        cadre_cursor.delete_one({"_id": delete_id})
        await ctx.send(f'Member {member_name}({delete_id})\'s application has been removed!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group ca - remove used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Cadre(bot))
