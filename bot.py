from cogs.quiz import quiz_start, quiz_end
from discord.ext import commands
from core.setup import jdata, client
import core.functions as func
import discord
import asyncio
import sqlite3
import json
import sys
import os
# import keep_alive


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)


@bot.event
async def on_ready():
    print(">> Bot is online <<")


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def load(ctx, msg):
    try:
        bot.load_extension(f'cogs.{msg}')
        await ctx.send(f':white_check_mark: Extension {msg} loaded.')
    except:
        await ctx.send(f':exclamation: There are no extension called {msg}!')


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def unload(ctx, msg):
    try:
        bot.unload_extension(f'cogs.{msg}')
        await ctx.send(f':white_check_mark: Extension {msg} unloaded.')
    except:
        await ctx.send(f':exclamation: There are no extension called {msg}!')


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def reload(ctx, msg):
    if msg != 'all':
        try:
            bot.reload_extension(f'cogs.{msg}')
            await ctx.send(f':white_check_mark: Extension {msg} reloaded.')
        except:
            await ctx.send(f':exclamation: There are no extension called {msg}!')
    else:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                bot.reload_extension(f'cogs.{filename[:-3]}')

    await ctx.send(':white_check_mark: Reload finished!')


@bot.command()
@commands.has_any_role('總召')
async def safe_stop(ctx):

    await ctx.send(':white_check_mark: The bot has stopped!')
    sys.exit(0)


@bot.event
async def on_disconnect():
    print('Bot disconnected')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# keep_alive.keep_alive()

bot.run(os.environ.get("TOKEN"))
