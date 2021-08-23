import discord
from discord.ext import commands
from ..core.cog_config import CogExtension


class Main(CogExtension):
    # bot info
    @commands.command()
    async def info(self, ctx):
        """cmd
        查詢SQCS_bot的資料。
        """
        embed = discord.Embed(
            title='Bot information',
            colour=self.bot.user.colour
        )
        embed.set_thumbnail(url="https://i.imgur.com/MbzRNTJ.png")
        embed.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url)

        embed.add_field(
            name='Join Time',
            value=f'Joined at {self.bot.user.created_at}'
        )
        embed.add_field(
            name='Source Code',
            value='https://github.com/phantom0174/SQCS_bot'
        )
        await ctx.send(embed=embed)

    # ping
    @commands.command()
    async def ping(self, ctx):
        """cmd
        戳一下機器人。
        """
        await ctx.send(f':stopwatch: {round(self.bot.latency * 1000)} (ms)')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def fix_role(self, ctx):
        """cmd
        手動修復身分組。
        """
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
                    except BaseException:
                        pass
                    break
        await ctx.send(':white_check_mark: 身分組維修完成！')

    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def findvname(self, ctx, name: str):
        for member in ctx.guild.members:
            member_name = member.name

            if member_name.find(name) != -1:
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
