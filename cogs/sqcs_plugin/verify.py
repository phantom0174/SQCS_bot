from discord.ext import commands
from core.cog_config import CogExtension
from random import randint
from core.mail import send_email
from core.db import self_client
from core.utils import Time


"""
This extension is currently not in use.
"""


class Verify(CogExtension):
    @commands.command()
    @commands.has_any_role('總召', 'Administrator')
    async def lect_generate_token(self, ctx, lecture_week: int, *, accounts):
        lect_set_cursor = self_client['LectureSetting']
        lect_data = lect_set_cursor.find_one({"week": lecture_week})
        if not lect_data:
            return await ctx.send(f":x: There's no lecture on week {lecture_week}")

        lecture_name = lect_data['name']
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

                with open('./assets/email/external_lecture_template.txt', mode='r', encoding='utf8') as template:
                    content = template.read() \
                            .replace('{time_stamp}', Time.get_info('partial')) \
                            .replace('{lect_name}', lecture_name) \
                            .replace('{lect_token}', token)

                    await send_email(
                        to_account=account,
                        subject='SQCS 講座加分神奇密碼',
                        content=content
                    )
            except:
                return await ctx.send(f":x: Error when sending {account}'s token email")

        await ctx.send(':white_check_mark: Token emails send!')


def setup(bot):
    bot.add_cog(Verify(bot))
