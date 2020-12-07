from discord.ext import commands
from cogs.setup import *
from functions import *
#import keep_alive
import discord
import asyncio
import sys
import os


intents = discord.Intents.all()

bot = commands.Bot(command_prefix='+', intents=intents)


@bot.event
async def on_ready():
    print(">> Bot is online <<")
    await GAU() #guild auto update


async def GAU():
    guild = bot.guilds[0]
    while(1):
        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if(now_time_info('date') == 1 and now_time_info('hour') >= 6 and quiz_data['event_status'] == 'False'):
            await quiz_start(guild)
            await getChannel(bot, '_Report').send(f'[Auto]Quiz event start. {now_time_info("whole")}')
        elif(now_time_info('date') == 7 and now_time_info('hour') >= 11 and quiz_data['event_status'] == 'True'):
            await quiz_end(guild)
            await getChannel(bot, '_Report').send(f'[Auto]Quiz event end. {now_time_info("whole")}')
        if(now_time_info('date') >= 1 and now_time_info('date') <= 5 and quiz_data['event_status'] == 'True' and quiz_data['stand_by_ans'] == 'N/A'):
            member = await bot.fetch_user(610327503671656449)
            await member.send('My master, the correct answer hasn\'t been set yet!')

        await asyncio.sleep(600)

# auto start quiz event
async def quiz_start(guild):
    main_channel = discord.utils.get(guild.text_channels, name='懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='◉總指令區')

    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()

    quiz_data['event_status'] = "True"
    quiz_data['correct_ans'] = quiz_data['stand_by_ans']
    quiz_data['stand_by_ans'] = 'N/A'

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')

    await main_channel.send('@everyone，有一個新的懸賞活動開始了，請確認你的答案是隱蔽模式！\n (請在答案的前方與後方各加上"||"的符號)')
    await main_channel.send(f'活動開始於 {now_time_info("whole")}')
    await main_channel.set_permissions(guild.default_role, send_messages=True)

    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()

# auto end quiz event
async def quiz_end(guild):
    main_channel = discord.utils.get(guild.text_channels, name='懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='◉總指令區')

    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()

    quiz_data['event_status'] = "False"
    quiz_data['correct_ans'] = "N/A"

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
    await main_channel.set_permissions(guild.default_role, send_messages=False)
    await main_channel.send(f'活動結束於 {now_time_info("whole")}')

    winners = str()
    for winner in quiz_data["correct_ans_member"]:
        member = await bot.fetch_user(winner)
        winners += f'{member.name}\n'

    if (winners == ''):
        winners += 'None'

    quiz_data['answered_member'].clear()

    await main_channel.send(embed=create_embed('Quiz Event Result', 0x42fcff, ['Winner'], [winners]))

    await getChannel(bot, '_ToMV').send('update_guild_fluctlight')


@bot.command()
async def safe_stop(ctx):
    if (role_check(ctx.author.roles, ['總召']) == False):
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
    bot.load_extension(f'cogs.{msg}')

@bot.command()
async def unload(ctx, msg):

    bot.unload_extension(f'cogs.{msg}')

@bot.command()
async def reload(ctx, msg):
    bot.reload_extension(f'cogs.{msg}')


for filename in os.listdir('./cogs'):
    if(filename.endswith('.py') and filename != 'setup.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

#keep_alive.keep_alive()

bot.run(os.environ.get("TOKEN"))