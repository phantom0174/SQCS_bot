from discord.ext import commands
from functions import *
#import keep_alive
import discord
import asyncio
import random
import json
import os


with open('jsons/setting.json', mode='r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='+', intents=intents)


@bot.event
async def on_ready():
    print(">> Bot is online <<")


async def main_autotask():
    guild = bot.guilds[0]
    while(1):
        temp_file = open('quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if(now_time_info('date') == 1 and now_time_info('hour') >= 6 and quiz_data['event_status'] == 'False'):
            await start(guild)
        elif(now_time_info('date') == 7 and now_time_info('hour') >= 11 and quiz_data['event_status'] == 'True'):
            await end(guild)

        if(now_time_info('date') >= 1 and now_time_info('date') <= 5 and quiz_data['event_status'] == 'True' and quiz_data['stand_by_ans'] == 'N/A'):
            member = await bot.fetch_user(610327503671656449)
            await member.send('My master, the correct answer hasn\'t been set yet!')

        await asyncio.sleep(600)



# ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'{round(bot.latency * 1000)} (ms)')


# main group of picture
@bot.group()
async def pic(ctx):
    pass


# ===== group - picture =====>>
# picture_manipulation
@pic.command()
async def p_m(ctx, *, msg):
    await ctx.message.delete()

    if (role_check(ctx.author.roles, '總召') == False):
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


# picture_check
@pic.command()
async def p_check(ctx):
    await ctx.message.delete()
    temp_file = open('jsons/setting.json', mode='r', encoding='utf8')
    setting_data = json.load(temp_file)
    temp_file.close()

    pic_str = str()

    for i in range(len(setting_data['pic'])):
        pic_str += str(i) + ': ' + setting_data['pic'][i]
        pic_str += '\n'

    await ctx.send(pic_str)


# random picture
@pic.command()
async def rpic(ctx):
    await ctx.message.delete()
    randPic = random.choice(jdata['pic'])
    await ctx.send(randPic)


# ===== group - picture =====<<

# member check
@bot.command()
async def m_check(ctx):
    for member in ctx.guild.members:
        print(member)


# ===== group - event =====>>
# main group of event command
@bot.group()
async def quiz(ctx):
    pass


# push back stand by answer
@quiz.commands()
async def push_back(ctx, msg):
    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()

    if(role_check(ctx.author.roles, '總召') == False):
        await ctx.send('You can\'t use this command!')
        return

    if(quiz_data['stand_by_ans'] != 'N/A'):
        await ctx.send(f'The stand-by answer had already been set as {quiz_data["stand_by_ans"]}!')
        return

    quiz_data['stand_by_ans'] = msg.content

    await ctx.send(f'The stand-by answer has been set as {quiz_data["stand_by_ans"]}!')

    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


# auto start quiz event
async def start(guild):
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

    await main_channel.send('@here，有一個新的懸賞活動開始了，請確認你的答案是隱蔽模式！\n (請在答案的前方與後方各加上"||"的符號)')
    await main_channel.send(f'活動開始於 {now_time_info("whole")}')
    await main_channel.set_permissions(guild.default_role, send_messages=True)

    print(quiz_data)
    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


# auto end quiz event
async def end(guild):
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
        user = await bot.fetch_user(int(winner))
        winners += user.display_name
        winners += '\n'

    if (winners == ''):
        winners += 'none'

    quiz_data['answered_member'].clear()

    embed = discord.Embed(title="Quiz Event Result", color=0x42fcff)
    embed.set_thumbnail(url="https://i.imgur.com/26skltl.png")
    embed.add_field(name="Winner", value=winners, inline=False)
    embed.set_footer(text=now_time_info("whole"))
    await main_channel.send(embed=embed)


# ===== group - event =====<<

# event answer listen function
@bot.listen()
async def on_message(msg):
    if (msg.channel.id != 746014424086610012):
        return

    if (msg.author == bot.user or msg.content[0] == '+' or msg.content[0] == '~'):
        return

    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()
    print(quiz_data)

    if (quiz_data["event_status"] == 'False'):
        return

    await msg.delete()
    print(msg.content[0:2], msg.content[-2:], msg.content[2:-2])
    if (msg.content[0:2] == '||' and msg.content[-2:] == '||'):
        answered = int(0)
        for answered_member_id in quiz_data['answered_member']:
            if (str(msg.author.id) == answered_member_id):
                await msg.author.send('你已經傳送過答案了，請不要重複傳送！')
                answered = int(1)
                break

        if (answered == int(0)):
            await msg.author.send('我收到你的答案了!')
            quiz_data["answered_member"].append(str(msg.author.id))
            if (msg.content[2:-2] == quiz_data["correct_ans"]):
                coni_channel = discord.utils.get(msg.guild.text_channels, name='bot-coni')
                await coni_channel.send(f'mv!score mani {msg.author.id} quiz_crt')
                quiz_data["correct_ans_member"].append(str(msg.author.id))
    else:
        await msg.author.send('你的答案是錯誤的格式！')


    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


# ===== group - lecture =====>>
@bot.group()
async def lect(ctx):
    pass

@lect.command()
async def start(ctx):

    if (role_check(ctx.author.roles, '總召') == False):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
    lecture_data = json.load(temp_file)
    temp_file.close()

    if(lecture_data['status'] == '1'):
        await ctx.send('The lecture has already started!')
        return

    await ctx.send('@here, the lecture has started!')

    lecture_data['status'] = '1'

    temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
    json.dump(lecture_data, temp_file)
    temp_file.close()

    msg_logs = await ctx.channel.history(limit=200).flatten()
    for msg in msg_logs:
        if(msg.content[0] == '&'):
            await msg.delete()

    # cd time from preventing member leave at once
    random.seed(now_time_info('hour')*92384)
    await asyncio.sleep(random.randint(30, 180))

    # add score to the attendances
    voice_channel = discord.utils.get(ctx.guild.voice_channels, name='星期五晚上固定講座')
    coni_channel = discord.utils.get(ctx.guild.text_channels, name='bot-coni')
    for member in voice_channel.members:
        await coni_channel.send(f'mv!score mani {member.id} lecture')



#lecture ans check
@lect.command()
async def ans_check(ctx, *, msg):
    Ans = msg.content.split(' ')
    msg_logs = await ctx.channel.history(limit=100).flatten()
    MemberCrtMsg = [] # correct message
    for msg in msg_logs:
        if(msg.author.bot == 'False' and msg.content[0] == '&'):
            for ans in Ans:
                if(msg.find(ans) != -1):
                    MemberCrtMsg.insert(0, msg)
                    await msg.delete()
                    break

    temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
    l_data = json.load(temp_file) #lecture data
    temp_file.close()

    temp_file = open('jsons/score_parameters.json', mode='r', encoding='utf8')
    sp_data = json.load(temp_file)  # score parameters data
    temp_file.close()

    Score = int(5)
    for crt_msg in MemberCrtMsg:
        IdIndex = int(-1)
        try:
            IdIndex = l_data['crt_member_id'].index(str(crt_msg.author.id))
        except:
            pass

        if(IdIndex > -1):
            l_data['crt_member_times'][IdIndex] = str(int(l_data['crt_member_times'][IdIndex]) + 1)
            l_data['crt_member_score'][IdIndex] = str(int(l_data['crt_member_score'][IdIndex]) + int(sp_data['point_weight'])*Score)
        else:
            l_data['crt_member_id'].append(str(crt_msg.author.id))
            l_data['crt_member_times'].append('1')
            l_data['crt_member_score'].append(str(int(sp_data['point_weight'])*Score))


        if (Score > 1):
            Score -= 1

    temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
    json.dump(l_data, temp_file)
    temp_file.close()


@lect.command()
async def end(ctx):

    if (role_check(ctx.author.roles, '總召') == False):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
    lecture_data = json.load(temp_file)
    temp_file.close()

    if (lecture_data['status'] == '0'):
        await ctx.send('The lecture has already ended!')
        return

    await ctx.send('@here, the lecture has ended!')

    lecture_data['status'] = '0'

    temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
    json.dump(lecture_data, temp_file)
    temp_file.close()

    answerer = str()

    temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
    l_data = json.load(temp_file)  # lecture data
    temp_file.close()

    for i in range(len(l_data['crt_member_id'])):
        member = (await ctx.guild.fetch_member(int(l_data['crt_member_id'][i]))).name
        times = l_data['crt_member_times'][i]
        score = l_data['crt_member_score'][i]
        answerer += f'{member}: {times}(times), {score}(score)\n'

    l_data['crt_member_id'].clear()
    l_data['crt_member_times'].clear()
    l_data['crt_member_score'].clear()


    embed = discord.Embed(title="Lecture Event Result", color=0x42fcff)
    embed.set_thumbnail(url="https://i.imgur.com/26skltl.png")
    embed.add_field(name="Answerer", value=answerer, inline=False)
    embed.set_footer(text=now_time_info("whole"))
    await ctx.send(embed=embed)

    temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
    json.dump(l_data, temp_file)
    temp_file.close()
# ===== group - lecture =====<<

'''
#bots communication event
@bot.listen()
async def on_message(ctx):
    if(ctx.author.bot == 'False' and ctx.author == bot.user):
        return

    MsgContent = str(ctx.content).split(' ')
    if(MsgContent[0] == 'SQCS'):
'''

#keep_alive.keep_alive()

bot.run(os.environ.get("TOKEN"))
