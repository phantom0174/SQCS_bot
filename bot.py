import discord
from discord.ext import commands
import json
import random
from functions import *


with open('setting.json', mode='r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='+', intents=intents)


@bot.event
async def on_ready():
    print(">> Bot is online <<")


"""
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(jdata['Cmd_channel']))
    await channel.send(f'{member} join!')

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(int(jdata['Cmd_channel']))
    await channel.send(f'{member} leave!')
"""


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
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    if (len(msg.split(' ')) > 2):
        await ctx.send('Too many arguments!')
        return

    if (len(msg.split(' ')) == 1):
        await ctx.send('There are no selected target!')
        return

    await msg.delete()

    temp_file = open('setting.json', mode='r', encoding='utf8')
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
    temp_file = open('setting.json', mode='w', encoding='utf8')
    json.dump(setting_data, temp_file)
    temp_file.close()


# picture_check
@pic.command()
async def p_check(ctx):
    await ctx.message.delete()
    temp_file = open('setting.json', mode='r', encoding='utf8')
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
async def event(ctx):
    pass


# start quiz event
@event.command()
async def start(ctx, msg):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()

    quiz_data['event_status'] = "True"
    quiz_data['correct_ans'] = str(msg)

    await ctx.channel.send(
        f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
    channel = discord.utils.get(ctx.guild.text_channels, name='懸賞區')
    await channel.send('@here，有一個新的懸賞活動開始了，請確認你的答案是隱蔽模式！\n (請在答案的前方與後方各加上"||"的符號)')

    await channel.send(f'活動開始於 {now_time()}')
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)

    print(quiz_data)
    temp_file = open('quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


# end quiz event
@event.command()
async def end(ctx):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()
    print(quiz_data)

    if (quiz_data['event_status'] == "False"):
        await ctx.send('沒有任何進行中的活動！')
        return

    quiz_data['event_status'] = "False"
    quiz_data['correct_ans'] = "N/A"

    # await ctx.send(f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
    channel = discord.utils.get(ctx.guild.text_channels, name='懸賞區')
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)

    await ctx.send(f'活動結束於 {now_time()}')

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
    embed.set_footer(text=now_time())
    await ctx.send(embed=embed)

    # adding scores to score.json
    stemp_file = open('score.json', mode='r', encoding='utf8')
    score_data = json.load(stemp_file)
    stemp_file.close()
    print(score_data)

    # opening score parameters
    sptemp_file = open('score_parameters.json', mode='r', encoding='utf8')
    para = json.load(sptemp_file)
    sptemp_file.close()

    earned_score = int(para['quiz_event_point'])*int(para['point_weight'])

    for correct_member in quiz_data['correct_ans_member']:
        user_log = int(0)
        for i in range(len(score_data['member_id'])):
            if (score_data['member_id'][i] == str(correct_member)):
                score_data['member_score'][i] = str(int(score_data['member_score'][i]) + earned_score)
                user_log = int(1)
                break

        if (user_log == int(0)):
            score_data['member_id'].append(str(correct_member))
            score_data['member_score'].append(str(earned_score))

    quiz_data['correct_ans_member'].clear()

    print(quiz_data)
    stemp_file = open('quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, stemp_file)
    stemp_file.close()

    print(score_data)
    temp_file = open('score.json', mode='w', encoding='utf8')
    json.dump(score_data, temp_file)
    temp_file.close()


# ===== group - event =====<<

# event answer listen function
@bot.listen()
async def on_message(msg):
    if (msg.channel.id != 746014424086610012):
        return

    if (msg.author == bot.user or msg.content[0] == '+' or msg.content[0] == '~'):
        return

    temp_file = open('quiz.json', mode='r', encoding='utf8')
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
                quiz_data["correct_ans_member"].append(str(msg.author.id))
    else:
        await msg.author.send('你的答案是錯誤的格式！')

    print(quiz_data)
    temp_file = open('quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


# ===== group - score =====>>
@bot.group()
async def score(ctx):
    pass


# scoreboare show
@score.command()
async def sb(ctx):
    if (ctx.author == bot.user):
        return

    temp_file = open('score.json', mode='r', encoding='utf8')
    score_data = json.load(temp_file)
    temp_file.close()
    print(score_data)

    if (len(score_data['member_score']) == 0):
        await ctx.send('The score board is empty!')
        return

    rank_index = []
    top = int(max(score_data['member_score']))
    while (top >= 0):
        for i in range(len(score_data['member_score'])):
            if (int(score_data['member_score'][i]) == top):
                rank_index.append(i)
        top -= 1

    score_board = str()
    for i in range(len(rank_index)):
        user = await bot.fetch_user(int(score_data['member_id'][rank_index[i]]))
        name = user.display_name
        score_board += name + ": " + score_data['member_score'][rank_index[i]]
        score_board += '\n'

    embed = discord.Embed(title="Score Board", color=0xffcd82)
    embed.set_thumbnail(url="https://i.imgur.com/26skltl.png")
    embed.add_field(name="Member score", value=score_board, inline=False)
    embed.set_footer(text=now_time())
    await ctx.send(embed=embed)


# score_manipulation
@score.command()
async def s_m(ctx, *, msg):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    if (len(msg.split(' ')) > 2):
        await ctx.send('Too many arguments!')
        return

    mScore = msg.split(' ')[0]
    userId = msg.split(' ')[1]
    user_s = int(0)

    temp_file = open('score.json', mode='r', encoding='utf8')
    score_data = json.load(temp_file)
    temp_file.close()

    m_bool = int(0)
    for i in range(len(score_data['member_id'])):
        if (score_data['member_id'][i] == userId):
            score_data['member_score'][i] = str(int(score_data['member_score'][i]) + mScore)
            user_s = int(score_data['member_score'][i]) + mScore
            m_bool = int(1)
            break

    if (m_bool == 0):
        await ctx.send(f'There are no member who\'s id is {userId} in the score board!')
    elif (m_bool == 1):
        await ctx.send(f'Success manipulating member\'s score to {user_s}!')

    print(score_data)
    temp_file = open('score.json', mode='w', encoding='utf8')
    json.dump(score_data, temp_file)
    temp_file.close()
# ===== group - score =====<<


# ===== group - lecture =====>>
@bot.group()
async def lect(ctx):
    pass

@lect.command()
async def start(ctx):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('lecture.json', mode='r', encoding='utf8')
    lecture_data = json.load(temp_file)
    temp_file.close()

    if(lecture_data['status'] == '1'):
        await ctx.send('The lecture has already started!')
        return

    await ctx.send('@here, the lecture has started!')

    lecture_data['status'] = '1'

    temp_file = open('lecture.json', mode='w', encoding='utf8')
    json.dump(lecture_data, temp_file)
    temp_file.close()

    msg_logs = await ctx.channel.history(limit=200).flatten()
    for msg in msg_logs:
        if(msg.content[0] == '&'):
            await msg.delete()



#lecture ans check
@lect.command()
async def ans_check(ctx, *, msg):
    Ans = msg.content.split(' ')
    msg_logs = await ctx.channel.history(limit=100).flatten()
    MemberCrtMsg = [] #correct message
    for msg in msg_logs:
        if(msg.author.bot == 'False' and msg.content[0] == '&'):
            for ans in Ans:
                if(msg.find(ans) != -1):
                    MemberCrtMsg.insert(0, msg)
                    await msg.delete()
                    break

    temp_file = open('lecture.json', mode='r', encoding='utf8')
    l_data = json.load(temp_file) #lecture data
    temp_file.close()

    temp_file = open('score_parameters.json', mode='r', encoding='utf8')
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

    temp_file = open('lecture.json', mode='w', encoding='utf8')
    json.dump(l_data, temp_file)
    temp_file.close()


@lect.command()
async def end(ctx):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    temp_file = open('lecture.json', mode='r', encoding='utf8')
    lecture_data = json.load(temp_file)
    temp_file.close()

    if (lecture_data['status'] == '0'):
        await ctx.send('The lecture has already ended!')
        return

    await ctx.send('@here, the lecture has ended!')

    lecture_data['status'] = '0'

    temp_file = open('lecture.json', mode='w', encoding='utf8')
    json.dump(lecture_data, temp_file)
    temp_file.close()

    answerer = str()

    temp_file = open('lecture.json', mode='r', encoding='utf8')
    l_data = json.load(temp_file)  # lecture data
    temp_file.close()

    for i in range(len(l_data['crt_member_id'])):
        member = (await ctx.guild.fetch_member(int(l_data['crt_member_id'][i]))).name
        times = l_data['crt_member_times'][i]
        score = l_data['crt_member_score'][i]
        answerer += f'{member}: {times}(times), {score}(score)\n'


    embed = discord.Embed(title="Lecture Event Result", color=0x42fcff)
    embed.set_thumbnail(url="https://i.imgur.com/26skltl.png")
    embed.add_field(name="Answerer", value=answerer, inline=False)
    embed.set_footer(text=now_time())
    await ctx.send(embed=embed)



# ===== group - lecture =====<<




"""
@bot.listen()
async def on_message(msg):
    if(msg.author == bot.user):
        return

    if(msg.content.find('hi') != -1):
        await msg.channel.send('i got it!')

@bot.command()
async def sayd(ctx, *, msg):
    await ctx.message.delete()
    await ctx.send(msg)
"""

'''acceptible
@bot.listen()
async def on_message(ctx):
    if(ctx.author.bot == 'False' and ctx.author == bot.user):
        return

    MsgContent = str(ctx.content).split(' ')
    if(MsgContent[0] == 'SQCS'):
'''


bot.run(jdata['TOKEN'])