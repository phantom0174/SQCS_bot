import os
from discord.ext import commands
import discord
from .core import utils as utl


class SQCSBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix='+',
            intents=intents,
            case_insensitive=True,
            self_bot=False,
            owner_id=610327503671656449
        )

    def setup(self):
        # load extensions
        for filename in os.listdir('./bot/cogs'):
            # normal cog file
            # if filename.find('.') != -1:
            if filename.endswith('.py'):
                # soft handling
                try:
                    super().load_extension(f'bot.cogs.{filename[:-3]}')
                except Exception as e:
                    print(f'Error loading bot.cogs.{filename[:-3]}')
                    print(e)
            elif filename.find('.') == -1:
                for sub_filename in os.listdir(f'./bot/cogs/{filename}'):
                    if sub_filename.endswith('.py'):
                        try:
                            super().load_extension(f'bot.cogs.{filename}.{sub_filename[:-3]}')
                        except Exception as e:
                            print(f'Error loading bot.cogs.{filename}.{sub_filename[:-3]}')
                            print(e)

    def run(self):
        self.setup()

        token = os.environ.get("BOT_TOKEN")
        super().run(token)

    async def on_ready(self):
        print(">--->> Bot is online <<---<")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name='+help'
            )
        )

    async def on_disconnect(self):
        report_channel = super().get_channel(785146879004508171)
        await report_channel.send(f':exclamation: Bot disconnected! {utl.Time.get_info("whole")}')
