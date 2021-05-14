from discord.ext import commands
from core.cog_config import CogExtension


class Main(CogExtension):
    # ping
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f':stopwatch: {round(self.bot.latency * 1000)} (ms)')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def fix_role(self, ctx):
        decline_lvl_roles = [
            ctx.guild.get_role(840633610256121867),
            ctx.guild.get_role(823804274647236618),
            ctx.guild.get_role(823804080199565342),
            ctx.guild.get_role(823803958052257813),
        ]
        for member in ctx.guild.members:
            if member.bot:
                continue

            for index, lvl_role in enumerate(decline_lvl_roles):
                if member.top_role.position > lvl_role.position:
                    for other_roles in decline_lvl_roles[index::]:
                        if other_roles in member.roles:
                            await member.remove_roles(other_roles)

                    try:
                        await member.add_roles(lvl_role)
                    except:
                        pass
                    break
        await ctx.send(':white_check_mark: 身分組維修完成！')

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
