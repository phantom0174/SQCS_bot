from discord.ext import commands
import core.functions as func
import discord
import sys
import os
import keep_alive


intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)


@bot.event
async def on_ready():
    print(">> Bot is online <<")


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def load(ctx, msg):
    await func.report_cmd(bot, ctx, f'[CMD EXECUTED][N/A][load]')

    try:
        bot.load_extension(f'cogs.{msg}')
        await ctx.send(f':white_check_mark: Extension {msg} loaded.')
    except:
        await ctx.send(f':exclamation: There are no extension called {msg}!')


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def unload(ctx, msg):
    await func.report_cmd(bot, ctx, f'[CMD EXECUTED][N/A][unload]')

    try:
        bot.unload_extension(f'cogs.{msg}')
        await ctx.send(f':white_check_mark: Extension {msg} unloaded.')
    except:
        await ctx.send(f':exclamation: There are no extension called {msg}!')


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def reload(ctx, msg):
    await func.report_cmd(bot, ctx, f'[CMD EXECUTED][N/A][reload]')

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
    await func.report_cmd(bot, ctx, f'[CMD EXECUTED][N/A][safe_stop]')

    await ctx.send(':white_check_mark: The bot has stopped!')
    sys.exit(0)


@bot.event
async def on_disconnect():
    print('Bot disconnected')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

keep_alive.keep_alive()

bot.run(os.environ.get("TOKEN"))
