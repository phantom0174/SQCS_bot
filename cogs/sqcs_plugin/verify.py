from discord.ext import commands
from core.cog_config import CogExtension
from random import randint
from core.mail import send_email


"""
This extension is currently not in use.
"""


class Verify(CogExtension):
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def lect_generate_token(self, ctx, *, accounts):
        accounts = accounts.split('\n')
        while ' ' in accounts:
            accounts.remove(' ')

        def generate(name):
            prefix = name[0]
            suffix = str(randint(
                randint(pow(2, 6), pow(2, 10)),
                randint(pow(2, 20), pow(2, 40)),
            ))
            return f'{prefix}{suffix}'

        # encryption (?
        token = [generate(name) for name in accounts.copy().split('@')]
        for (account, token) in zip(accounts, token):
            try:
                await send_email(
                    to_account=account,
                    subject='SQCS 講座加分神奇密碼',
                    content=f'請在 #講座加分 頻道中輸入以下指令，就可以獲得今天的講座分數！'
                            f'+lect verify {token}'
                            f'之後也要來聽講座呦！\\^~^'
                )
            except:
                return ctx.send(f":x: Error when sending {account}'s token email")

        await ctx.send(':white_check_mark: Token emails send!')


def setup(bot):
    bot.add_cog(Verify(bot))
