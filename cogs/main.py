from discord.ext import commands
from core.cog_config import CogExtension


class Main(CogExtension):
    # ping
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f':stopwatch: {round(self.bot.latency * 1000)} (ms)')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def give_default_role(self, ctx):
        common_role = ctx.guild.get_role(823803958052257813)
        for member in ctx.guild.members:
            if len(member.roles) == 1 and member.roles[0].name == '@everyone':
                await member.add_roles(common_role)

        await ctx.send(':white_check_mark: Operation finished!')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvname(self, ctx, search_via_name: str):

        for member in ctx.guild.members:
            member_name = member.name

            if member_name.find(search_via_name) != -1:
                await ctx.send(f'{member_name} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvnick(self, ctx, search_via_nick: str):

        for member in ctx.guild.members:
            member_nick = member.nick
            if member_nick is None:
                continue

            if member_nick.find(search_via_nick) != -1:
                await ctx.send(f'{member_nick} {member.id}')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvid(self, ctx, search_via_id: int):

        for member in ctx.guild.members:
            if member.id != search_via_id:
                continue

            if member.name is None:
                return await ctx.send(f'{member.name} {member.id}')

            await ctx.send(f'{member.nick} {member.id}')


def setup(bot):
    bot.add_cog(Main(bot))
