from discord.ext import commands
import discord
import sys
import os
from core import keep_alive
import asyncio
import core.utils as utl
import logging
from typing import Tuple
from dotenv import load_dotenv

# load token from .env
load_dotenv()


Format = '%(asctime)s %(levelname)s: %(message)s, ' \
         'via line: %(lineno)d, ' \
         'in func: %(funcName)s, ' \
         'of file: %(pathname)s\n'

logging.basicConfig(
    filename='./buffer/bot.log',
    level=logging.WARNING,
    format=Format
)
logging.captureWarnings(True)


intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix='+',
    intents=intents,
    case_insensitive=True,
    owner_id=610327503671656449
)


@bot.event
async def on_ready():
    print(">--->> Bot is online <<---<")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f'+help'
        )
    )


@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title='Bot information',
        colour=bot.user.colour
    )
    embed.set_thumbnail(url="https://i.imgur.com/MbzRNTJ.png")
    embed.set_author(name=bot.user.display_name, icon_url=bot.user.avatar_url)

    embed.add_field(
        name='Join Time',
        value=f'Joined at {bot.user.created_at}'
    )
    embed.add_field(
        name='Source Code',
        value='https://github.com/phantom0174/SQCS_bot'
    )
    await ctx.send(embed=embed)


# function for cogs management
def find_cog(target_cog: str, mode: str) -> Tuple[bool, str]:
    def load_ext(full_path: str):
        if mode == 'load':
            bot.load_extension(full_path)
        if mode == 'unload':
            bot.unload_extension(full_path)
        if mode == 'reload':
            bot.reload_extension(full_path)

    for find_filename in os.listdir('./cogs'):
        # normal cog file
        if find_filename.find('.') != -1:
            if find_filename.startswith(target_cog) and find_filename.endswith('.py'):
                load_ext(f'cogs.{find_filename[:-3]}')
                return True, f':white_check_mark: Extension {find_filename} {mode}ed!'
        else:
            for find_sub_filename in os.listdir(f'./cogs/{find_filename}'):
                if find_sub_filename.startswith(target_cog) and find_sub_filename.endswith('.py'):
                    load_ext(f'cogs.{find_filename}.{find_sub_filename[:-3]}')
                    return True, f':white_check_mark: Extension {find_sub_filename} {mode}ed!'
    return False, ''


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def load(ctx, target_cog: str):
    find, msg = find_cog(target_cog, 'load')
    if find:
        return await ctx.send(msg)

    return await ctx.send(
        f':exclamation: There are no extension called {target_cog}!'
    )


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def unload(ctx, target_cog: str):
    find, msg = find_cog(target_cog, 'unload')
    if find:
        return await ctx.send(msg)

    return await ctx.send(
        f':exclamation: There are no extension called {target_cog}!'
    )


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def reload(ctx, target_cog: str):
    find, msg = find_cog(target_cog, 'reload')
    if find:
        return await ctx.send(msg)

    return await ctx.send(
        f':exclamation: There are no extension called {target_cog}!'
    )


@bot.command(aliases=['logout', 'shutdown'])
@commands.has_any_role('總召')
async def shut_down(ctx):
    await ctx.send(':white_check_mark: The bot is shutting down...')
    await bot.logout()
    await asyncio.sleep(1)
    sys.exit(0)


@bot.event
async def on_disconnect():
    report_channel = bot.get_channel(785146879004508171)
    await report_channel.send(f':exclamation: Bot disconnected! {utl.Time.get_info("whole")}')


for filename in os.listdir('./cogs'):
    # normal cog file
    if filename.find('.') != -1:
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
    elif filename.find('.') == -1:
        for sub_filename in os.listdir(f'./cogs/{filename}'):
            if sub_filename.endswith('.py'):
                bot.load_extension(f'cogs.{filename}.{sub_filename[:-3]}')

keep_alive.keep_alive()

if __name__ == "__main__":
    bot.run(os.environ.get("BOT_TOKEN"))
