from discord.ext import commands
from core.cog_config import CogExtension
from random import randint
from core.mail import send_email
from core.db import self_client


"""
This extension is currently not in use.
"""


class Verify(CogExtension):
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def lect_generate_token(self, ctx, *, accounts):
        verify_cursor = self_client['Verification']

        accounts = accounts.split('\n')
        accounts = list(filter(lambda item: item.strip(), accounts))

        def generate(name):
            prefix = name[0]
            suffix = str(randint(
                randint(pow(2, 6), pow(2, 10)),
                randint(pow(2, 20), pow(2, 40)),
            ))
            return f'{prefix}{suffix}'

        # token generation
        tokens = [generate(name.split('@')) for name in accounts.copy()]
        for (account, token) in zip(accounts, tokens):
            try:
                token_data = {
                    "TOKEN": str(token),
                    "reason": 'lect'
                }
                verify_cursor.insert_one(token_data)

                await send_email(
                    to_account=account,
                    subject='SQCS 講座加分神奇密碼',
                    content=f'請在 #講座加分 頻道中輸入以下指令，就可以獲得今天的講座分數！\n'
                            f'+lect_verify attend {token}\n'
                            f'之後也要來聽講座呦！\\^~^'
                )
            except:
                return await ctx.send(f":x: Error when sending {account}'s token email")

        await ctx.send(':white_check_mark: Token emails send!')


def setup(bot):
    bot.add_cog(Verify(bot))
