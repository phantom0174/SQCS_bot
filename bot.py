from cogs.quiz import quiz_start, quiz_end
from discord.ext import commands
from core.setup import *
from functions import *
# import keep_alive
import discord
import asyncio
import sqlitebck # can only use on console
import sys
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='+', intents=intents)


@bot.event
async def on_ready():
    print(">> Bot is online <<")
    await setChannel(bot)
    await GAU()  # guild auto update


async def GAU():
    while True:
        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if now_time_info('date') == 1 and now_time_info('hour') >= 6 and quiz_data['event_status'] == 'False':
            await quiz_start(bot)
            await getChannel('_Report').send(f'[Auto]Quiz event start. {now_time_info("whole")}')
        elif now_time_info('date') == 7 and now_time_info('hour') >= 11 and quiz_data['event_status'] == 'True':
            await quiz_end(bot)
            await getChannel('_Report').send(f'[Auto]Quiz event end. {now_time_info("whole")}')

        if (1 <= now_time_info('date') <= 5) and quiz_data['event_status'] == 'True' and quiz_data['stand_by_ans'] == 'N/A':
            member = await bot.fetch_user(610327503671656449)
            await member.send('My master, the correct answer hasn\'t been set yet!')

        # db backup
        temp_file = open('jsons/dyn_setting.json', mode='r', encoding='utf8')
        dyn = json.load(temp_file)
        temp_file.close()

        if dyn['ldbh'] != now_time_info('hour'):
            file_name = 'db_backup/' + str(now_time_info('hour')) + '_backup.db'
            bck_db_conn = sqlite3.connect(file_name)
            sqlitebck.copy(connection, bck_db_conn)

            dyn['ldbh'] = now_time_info('hour')

            temp_file = open('jsons/dyn_setting.json', mode='w', encoding='utf8')
            json.dump(dyn, temp_file)
            temp_file.close()


        await asyncio.sleep(600)


@bot.command()
async def safe_stop(ctx):
    if not role_check(ctx.author.roles, ['總召']):
        await ctx.send('You can\'t use that command!')
        return

    print('The bot has stopped!')
    info.connection.commit()
    info.connection.close()
    sys.exit(0)


@bot.event
async def on_disconnect():
    print('Bot disconnected')
    info.connection.commit()


@bot.command()
async def load(ctx, msg):
    try:
        bot.load_extension(f'cogs.{msg}')
        await ctx.send(f'Extension {msg} loaded.')
    except:
        await ctx.send(f'There are no extension called {msg}!')


@bot.command()
async def unload(ctx, msg):
    try:
        bot.unload_extension(f'cogs.{msg}')
        await ctx.send(f'Extension {msg} unloaded.')
    except:
        await ctx.send(f'There are no extension called {msg}!')


@bot.command()
async def reload(ctx, msg):
    try:
        bot.reload_extension(f'cogs.{msg}')
        await ctx.send(f'Extension {msg} reloaded.')
    except:
        await ctx.send(f'There are no extension called {msg}!')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# keep_alive.keep_alive()

bot.run(os.environ.get("TOKEN"))
