from discord.ext import commands
import discord
import sys
import os
import keep_alive
import asyncio
import core.functions as func


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
        for reload_filename in os.listdir('./cogs'):
            if reload_filename.endswith('.py'):
                bot.reload_extension(f'cogs.{reload_filename[:-3]}')

        await ctx.send(':white_check_mark: Reload finished!')


@bot.command()
@commands.has_any_role('總召')
async def shut_down(ctx):
    await ctx.send(':white_check_mark: The bot is shutting down...')
    await bot.logout()
    await asyncio.sleep(1)
    sys.exit(0)


@bot.event
async def on_disconnect():
    report_channel = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-report')
    await report_channel.send(f':exclamation: Bot disconnected! {func.now_time_info("whole")}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')


keep_alive.keep_alive()

if __name__ == "__main__":
    bot.run(os.environ.get("TOKEN"))
