from discord.ext import commands
from functions import *
#import keep_alive
import statistics
import discord
import asyncio
import sqlite3
import random
import json
import sys
import os


with open('jsons/setting.json', mode='r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

connection = sqlite3.connect('DataBase.db')
info = connection.cursor()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='+', intents=intents)

global _ToSyn
global _ToMV
global _Report


def db_setup():

    info.execute("""CREATE TABLE IF NOT EXISTS quiz (
          Id INTEGER);""")

    info.execute("""CREATE TABLE IF NOT EXISTS lecture (
          Id INTEGER,
          Score REAL,
          Count INTEGER);""")

    info.connection.commit()

def create_embed(Title, Color, FieldsName, Values):
    embed = discord.Embed(title=Title, color=Color)
    embed.set_thumbnail(url="https://i.imgur.com/26skltl.png")
    if(len(FieldsName) != len(Values)):
        embed.add_field(name="Error", value='N/A', inline=False)
        return embed

    for i in range(len(FieldsName)):
        embed.add_field(name=FieldsName[i], value=Values[i], inline=False)

    embed.set_footer(text=now_time_info('whole'))
    return embed


@bot.event
async def on_ready():
    global _ToSyn
    global _ToMV
    global _Report

    # bot communicate channels
    _ToSyn = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-and-syn')
    _ToMV = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-and-mv')
    _Report = discord.utils.get(bot.guilds[1].text_channels, name='sqcs-report')

    print(">> Bot is online <<")
    db_setup()
    await GAU() #guild auto update


async def GAU():
    guild = bot.guilds[0]
    while(1):
        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if(now_time_info('date') == 1 and now_time_info('hour') >= 6 and quiz_data['event_status'] == 'False'):
            await quiz_start(guild)
            await _Report.send(f'[Auto]Quiz event start. {now_time_info("whole")}')
        elif(now_time_info('date') == 7 and now_time_info('hour') >= 11 and quiz_data['event_status'] == 'True'):
            await quiz_end(guild)
            await _Report.send(f'[Auto]Quiz event end. {now_time_info("whole")}')
        if(now_time_info('date') >= 1 and now_time_info('date') <= 5 and quiz_data['event_status'] == 'True' and quiz_data['stand_by_ans'] == 'N/A'):
            member = await bot.fetch_user(610327503671656449)
            await member.send('My master, the correct answer hasn\'t been set yet!')

        await asyncio.sleep(600)



# ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'{round(bot.latency * 1000)} (ms)')


# delete message
@bot.command()
async def clear(ctx, msg):
    number = int(msg) + 1
    msg_logs = await ctx.channel.history(limit=number).flatten()
    for msg in msg_logs:
        await msg.delete()

    await _Report.send(f'[Command]clear used by user {ctx.author.id}. {now_time_info("whole")}')


# main group of picture
@bot.group()
async def pic(ctx):
    pass


# ===== group - picture =====>>
# picture_manipulation
@pic.command()
async def p_m(ctx, *, msg):
    await ctx.message.delete()

    if (role_check(ctx.author.roles, ['總召', 'Administrator']) == False):
        await ctx.send('You can\'t use that command!')
        return

    if (len(msg.split(' ')) > 2):
        await ctx.send('Too many arguments!')
        return

    if (len(msg.split(' ')) == 1):
        await ctx.send('There are no selected target!')
        return

    await msg.delete()

    temp_file = open('jsons/setting.json', mode='r', encoding='utf8')
    setting_data = json.load(temp_file)
    temp_file.close()

    mode = msg.split(' ')[0]
    m_object = msg.split(' ')[1]

    if (mode == '0'):
        if (int(m_object) >= int(len(setting_data['pic']))):
            await ctx.send('Index out of range!')
            return

        del_object = setting_data['pic'][int(m_object)]
        del (setting_data['pic'][int(m_object)])
        await ctx.send(f'Object {del_object} successfully deleted!')
    elif (mode == '1'):
        setting_data['pic'].append(m_object)
        await ctx.send(f'Object {m_object} successfully added!')
    else:
        await ctx.send('Mode argument error!')

    print(setting_data)
    temp_file = open('jsons/setting.json', mode='w', encoding='utf8')
    json.dump(setting_data, temp_file)
    temp_file.close()

    await _Report.send(f'[Command]Group pic - p_m used by member {ctx.author.id}. {now_time_info("whole")}')


# picture_check
@pic.command()
async def p_check(ctx):
    await ctx.message.delete()
    temp_file = open('jsons/setting.json', mode='r', encoding='utf8')
    setting_data = json.load(temp_file)
    temp_file.close()

    pic_str = str()

    for i in range(len(setting_data['pic'])):
        pic_str += f'{i}: {setting_data["pic"][i]}\n'

    await ctx.send(pic_str)

    await _Report.send(f'[Command]Group pic - p_check used by member {ctx.author.id}. {now_time_info("whole")}')


# random picture
@pic.command()
async def rpic(ctx):
    await ctx.message.delete()
    randPic = random.choice(jdata['pic'])
    await ctx.send(randPic)

    await _Report.send(f'[Command]Group pic - rpic used by member {ctx.author.id}. {now_time_info("whole")}')


# ===== group - picture =====<<



# member check
@bot.command()
async def m_check(ctx):
    for member in ctx.guild.members:
        print(member)



# ===== group - event =====>>
@bot.group()
async def quiz(ctx):
    pass


# push back stand by answer
@quiz.command()
async def quiz_push(ctx, msg):
    if(role_check(ctx.author.roles, ['總召', 'Administrator']) == False):
        await ctx.send('You can\'t use this command!')
        return

    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()

    if(quiz_data['stand_by_ans'] != 'N/A'):
        await ctx.send(f'The stand-by answer had already been set as {quiz_data["stand_by_ans"]}!')
        return

    quiz_data['stand_by_ans'] = msg

    await ctx.send(f'The stand-by answer has been set as {quiz_data["stand_by_ans"]}!')

    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()

    await _Report.send(f'[Command]Group quiz - quiz_push used by member {ctx.author.id}. {now_time_info("whole")}')


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

    await cmd_channel.send(f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
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

    await _ToMV.send('update_guild_fluctlight')


# event answer listen function
@bot.listen()
async def on_message(msg):
    main_channel = discord.utils.get(bot.guilds[0].text_channels, name='懸賞區')
    if (msg.author == bot.user or msg.channel != main_channel or msg.content[0] == '~'):
        return

    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()
    print(quiz_data)

    if (quiz_data["event_status"] == 'False'):
        return

    await msg.delete()

    answered = int(-1)
    try:
        answered = quiz_data['answered_member'].index(msg.author.id)
    except:
        pass

    if (answered != -1):
        await msg.author.send('你已經傳送過答案了，請不要重複傳送！')
        return

    # print(msg.content[0:2], msg.content[-2:], msg.content[2:-2])
    if (msg.content[0:2] == '||' and msg.content[-2:] == '||'):
        await msg.author.send('我收到你的答案了!')
        quiz_data["answered_member"].append(msg.author.id)

        if (msg.content[2:-2] == quiz_data["correct_ans"]):
            await _ToMV.send(f'quiz_crt {msg.author.id}')
            await quiz_data['correct_ans_member'].append(msg.author.id)
    else:
        await msg.author.send('你的答案是錯誤的格式！')

    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()

# ===== group - event =====<<




# ===== group - lecture =====>>
@bot.group()
async def lect(ctx):
    pass


@lect.command()
async def start(ctx, *, msg):
    if (role_check(ctx.author.roles, ['總召', 'Administrator']) == False):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
    lecture_data = json.load(temp_file)
    temp_file.close()

    if (lecture_data['event_status'] == 'True'):
        await ctx.send('The lecture has already started!')
        return

    day = msg.split(' ')[0]

    await ctx.send('@everyone，講座開始了！\n 於回答講師問題時請在答案前方加上"&"，回答正確即可加分。')

    lecture_data['event_status'] = 'True'

    def check(message):
        return message.channel == _ToMV

    await _ToMV.send('request_score_weight')
    sw = int((await bot.wait_for('message', check=check, timeout=30.0)).content)

    lecture_data['temp_sw'] = sw

    temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
    json.dump(lecture_data, temp_file)
    temp_file.close()

    msg_logs = await ctx.channel.history(limit=200).flatten()
    for msg in msg_logs:
        if (len(msg.content) > 0 and msg.content[0] == '&'):
            await msg.delete()

    # cd time from preventing member leave at once
    random.seed(now_time_info('hour') * 92384)
    await asyncio.sleep(random.randint(30, 180))

    # add score to the attendances

    if(day == '5'):
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name='星期五晚上固定講座')
    elif(day == '7'):
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name='量子電腦硬體')

    for member in voice_channel.members:
        await _ToMV.send(f'lecture_attend {member.id}')

    await _Report.send(f'[Command]Group lect - start used by member {ctx.author.id}. {now_time_info("whole")}')


# lecture ans check
@lect.command()
async def ans_check(ctx, *, msg):
    CrtAns = msg.split(' ')
    msg_logs = await ctx.channel.history(limit=100).flatten()
    MemberCrtMsg = []  # correct message

    for msg in msg_logs:
        if (len(msg.content) == 0):
            continue

        if (msg.author.bot == False and msg.content[0] == '&'):
            await msg.delete()
            for ans in CrtAns:
                # correct answer is a subset of member answer
                if (msg.content.find(ans) != -1):
                    MemberCrtMsg.append(msg)
                    break

    MemberCrtMsg.reverse()


    # add score to correct members
    temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
    l_data = json.load(temp_file)  # lecture data
    temp_file.close()

    TScore = float(5)
    for crt_msg in MemberCrtMsg:
        TargetId = crt_msg.author.id
        mScore = TScore * float(l_data["temp_sw"])
        info.execute(f'SELECT Id, Score, Count FROM lecture WHERE Id={TargetId}')
        data = info.fetchall()

        if (len(data) == 0):
            info.execute(f'INSERT INTO lecture VALUES({TargetId}, {mScore}, 1);')
        else:
            old_Score = float(data[0][1])
            old_Count = int(data[0][2])

            info.execute(
                f'UPDATE lecture SET Score={old_Score + mScore}, Count={old_Count + 1} WHERE Id={TargetId};')

        if (TScore > 1):
            TScore -= 1

    info.connection.commit()

    await _Report.send(f'[Command]Group lect - ans_check used by member {ctx.author.id}. {now_time_info("whole")}')



@lect.command()
async def end(ctx):

    if (role_check(ctx.author.roles, ['總召', 'Administrator']) == False):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
    lecture_data = json.load(temp_file)
    temp_file.close()

    if (lecture_data['event_status'] == 'False'):
        await ctx.send('The lecture has already ended!')
        return

    await ctx.send('@here, the lecture has ended!')

    lecture_data['event_status'] = 'False'

    temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
    json.dump(lecture_data, temp_file)
    temp_file.close()

    # adding scores and show lecture final data
    info.execute("SELECT * FROM lecture ORDER BY Score DESC")
    data = info.fetchall()
    if (len(data) == 0):
        await ctx.send('There are no data to show!')
        return
    else:
        data_members = str()
        for member in data:
            member_obj = await bot.fetch_user(member[0])  # member id
            data_members += f'{member_obj.name}:: Score: {member[1]}, Answer Count: {member[2]}\n'
            await _ToMV.send(f'lect_crt {member[0]} {member[1]}')

        await ctx.send(embed=create_embed('Lecture Event Result', 0x42fcff, ['Lecture final info'], [data_members]))

    info.execute('DELETE FROM lecture')
    info.connection.commit()

    await _Report.send(f'[Command]Group lect - end used by member {ctx.author.id}. {now_time_info("whole")}')


# ===== group - lecture =====<<


# bots communication event
@bot.listen()
async def on_message(ctx):
    if(ctx.author.bot == 'False' or ctx.author == bot.user or (ctx.channel != _ToMV or ctx.channel != _ToSyn)):
        return

    MsgCont = str(ctx.content).split(' ')

    if(MsgCont[0] == 'sw' and ctx.channel == _ToMV):
        temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
        lect_data = json.load(temp_file)
        temp_file.close()

        lect_data['temp_sw'] = MsgCont[1]

        temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
        json.dump(lect_data, temp_file)
        temp_file.close()
        return


@bot.command()
async def msg_re(ctx, *, msg):
    re_msg = msg.split('\n')
    for msg in re_msg:
        await ctx.send(msg)

    await _Report.send(f'[Command]msg_re used by member {ctx.author.id}. {now_time_info("whole")}')


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

#keep_alive.keep_alive()

bot.run(os.environ.get("TOKEN"))