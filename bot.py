from discord.ext import commands
import discord
import sys
import os
import keep_alive
import asyncio
import core.utils as utl


intents = discord.Intents.all()
bot = commands.Bot(
    command_prefix='+',
    intents=intents,
    owner_id=610327503671656449
)


@bot.event
async def on_ready():
    print(">> Bot is online <<")


# a short function for load and unload cogs
def find_cog(path: str, target_cog: str, mode: str) -> (bool, str):
    trans_path = {
        "./cogs": "cogs.",
        "./cogs/sqcs_plugin": "cogs/sqcs."
    }
    for item in os.listdir(path):
        if item.startswith(target_cog) and item.endswith('.py'):
            if mode == 'load':
                bot.load_extension(
                    f'{trans_path.get(path)}{item[:-3]}'
                )
                return True, f':white_check_mark: Extension {item} loaded!'
            elif mode == 'unload':
                bot.unload_extension(
                    f'{trans_path.get(path)}{item[:-3]}'
                )
                return True, f':white_check_mark: Extension {item} unloaded!'
    return False, ''


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def load(ctx, target_cog: str):
    find, msg = find_cog('./cogs', target_cog, 'load')
    if find:
        return await ctx.send(msg)

    find, msg = find_cog('./cogs/sqcs_plugin', target_cog, 'load')
    if find:
        return await ctx.send(msg)

    return await ctx.send(
        f':exclamation: There are no extension called {target_cog}!'
    )


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def unload(ctx, target_cog: str):
    find, msg = find_cog('./cogs', target_cog, 'unload')
    if find:
        return await ctx.send(msg)

    find, msg = find_cog('./cogs/sqcs_plugin', target_cog, 'unload')
    if find:
        return await ctx.send(msg)

    return await ctx.send(
        f':exclamation: There are no extension called {target_cog}!'
    )


@bot.command()
@commands.has_any_role('總召', 'Administrator')
async def reload(ctx, target_package: str):
    if target_package not in ['main', 'sqcs']:
        return await ctx.send(
            ':x: `target_package` can only be `main` or `sqcs`!'
        )

    if target_package == 'all':
        for reload_filename in os.listdir('./cogs'):
            if reload_filename.endswith('.py'):
                bot.reload_extension(f'cogs.{reload_filename[:-3]}')
    elif target_package == 'sqcs':
        for reload_filename in os.listdir('./cogs/sqcs_plugin'):
            if reload_filename.endswith('.py'):
                bot.reload_extension(f'cogs/sqcs_plugin.{reload_filename[:-3]}')

    await ctx.send(':white_check_mark: Reload finished!')


@bot.command(aliases=['logout', 'shutdown'])
@commands.has_any_role('總召')
async def shut_down(ctx):
    await ctx.send(':white_check_mark: The bot is shutting down...')
    await bot.logout()
    await asyncio.sleep(1)
    sys.exit(0)


@bot.event
async def on_disconnect():
    report_channel = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-report')
    await report_channel.send(f':exclamation: Bot disconnected! {utl.Time.get_info("whole")}')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
for filename in os.listdir('./cogs/sqcs_plugin'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.sqcs_plugin.{filename[:-3]}')


keep_alive.keep_alive()

if __name__ == "__main__":
    bot.run(os.environ.get("TOKEN"))
