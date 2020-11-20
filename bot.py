import discord
from discord.ext import commands
import json
import random
from datetime import datetime,timezone,timedelta

def now_time():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
    return str(dt2.strftime("%Y-%m-%d %H:%M:%S"))


with open('setting.json', mode='r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

bot = commands.Bot(command_prefix='+')


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

#ping
@bot.command()
async def ping(ctx):
    await ctx.send(f'{round(bot.latency * 1000)} (ms)')

#random picture
@bot.command()
async def rpic(ctx):
    randPic = random.choice(jdata['pic'])
    await ctx.send(randPic)

#department role update
@bot.command()
async def role_update(ctx, *, msg):
    if (round(bot.latency * 1000) <= 100):
        await ctx.send('The bot is now hosting on repl.it, please host it on pc to use this command!')
        return

        # Mode:: 1:副召, 2:美宣, 3:網管, 4:公關, 5:議程, 6:管理
    print(msg.split(' '))
    if (len(msg.split(' ')) != 2):
        await ctx.send('There are no target selected!')
        return

    mode = int(msg.split(' ')[0])
    print(mode)

    msg_split = msg.split(' ')[1].split('\n')
    print(msg_split)

    if (int(len(msg_split)) % 2 != 0):
        await ctx.send('School -> Name map error!')
        return

    school = []
    name = []

    new_role = ctx.guild.get_role(int(jdata['department_id'][mode]))
    await ctx.send(new_role)

    for i in range(int(len(msg_split))):
        if (i + 1 <= int(len(msg_split) / 2)):
            school.append(msg_split[i])
        else:
            name.append(msg_split[i])

    for i in range(int(len(msg_split) / 2)):
        for member in ctx.guild.members:
            member_tag = member.name.split(' ')
            print(member_tag)

            if (len(member_tag) >= 3):
                member_school = member_tag[0]
                member_name = member_tag[1]
                if (member_school.find(school[i]) != -1 and member_name == name[i]):
                    old_role = member.top_role
                    if (len(member.roles) == 2):
                        await member.remove_roles(old_role)
                    await member.add_roles(new_role)
                    await ctx.channel.send(f'{member.name}\'s role was updated to {new_role}!')

    await ctx.send('Role update complete!')

#member check
@bot.command()
async def m_check(ctx):
    if (round(bot.latency * 1000) <= 100):
        await ctx.send('The bot is now hosting on repl.it, please host it on pc to use this command!')
        return

    for member in ctx.guild.members:
        print(member)

#start quiz event
@bot.command()
async def sqe(ctx, msg):
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

#end quiz event
@bot.command()
async def eqe(ctx):
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

    for correct_member in quiz_data['correct_ans_member']:
        user_log = int(0)
        for i in range(len(score_data['member_id'])):
            if (score_data['member_id'][i] == str(correct_member)):
                score_data['member_score'][i] = str(int(score_data['member_score'][i]) + 1)
                user_log = int(1)
                break

        if (user_log == int(0)):
            score_data['member_id'].append(str(correct_member))
            score_data['member_score'].append(str(1))

    quiz_data['correct_ans_member'].clear()

    print(quiz_data)
    stemp_file = open('quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, stemp_file)
    stemp_file.close()

    print(score_data)
    temp_file = open('score.json', mode='w', encoding='utf8')
    json.dump(score_data, temp_file)
    temp_file.close()

#scoreboare show
@bot.command()
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


#picture_manipulation
@bot.command()
async def p_m(ctx, *, msg):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    if(len(msg.split(' ')) > 2):
        await ctx.send('Too many arguments!')
        return

    if(len(msg.split(' ')) == 1):
        await ctx.send('There are no selected target!')
        return

    await msg.delete()

    temp_file = open('setting.json', mode='r', encoding='utf8')
    setting_data = json.load(temp_file)
    temp_file.close()

    mode = msg.split(' ')[0]
    m_object = msg.split(' ')[1]

    if(mode == '0'):
        if(int(m_object) >= int(len(setting_data['pic']))):
            await ctx.send('Index out of range!')
            return

        del_object = setting_data['pic'][int(m_object)]
        del(setting_data['pic'][int(m_object)])
        await ctx.send(f'Object {del_object} successfully deleted!')
    elif(mode == '1'):
        setting_data['pic'].append(m_object)
        await ctx.send(f'Object {m_object} successfully added!')
    else:
        await ctx.send('Mode argument error!')

    print(setting_data)
    temp_file = open('setting.json', mode='w', encoding='utf8')
    json.dump(setting_data, temp_file)
    temp_file.close()

#picture_check
@bot.command()
async def p_check(ctx):
    temp_file = open('setting.json', mode='r', encoding='utf8')
    setting_data = json.load(temp_file)
    temp_file.close()

    pic_str = str()

    for i in range(len(setting_data['pic'])):
        pic_str += str(i) + ': ' + setting_data['pic'][i]
        pic_str += '\n'

    await ctx.send(pic_str)

#score_manipulation
@bot.command()
async def s_m(ctx, *, msg):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)
            break

    if (role_bool == int(0)):
        await ctx.send('You can\'t use that command!')
        return

    if(len(msg.split(' ')) > 2):
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
        if(score_data['member_id'][i] == userId):
            score_data['member_score'][i] = str(int(score_data['member_score'][i]) + mScore)
            user_s = int(score_data['member_score'][i]) + mScore
            m_bool = int(1)
            break

    if(m_bool == 0):
        await ctx.send(f'There are no member who\'s id is {userId} in the score board!')
    elif(m_bool == 1):
        await ctx.send(f'Success manipulating member\'s score to {user_s}!')

    print(score_data)
    temp_file = open('score.json', mode='w', encoding='utf8')
    json.dump(score_data, temp_file)
    temp_file.close()


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


@bot.command()
async def info(ctx):
    embed = discord.Embed(title="Prefix = +", description="Ad as Administrator", color=0x32ec60)
    embed.set_author(name="Author: phantom0174", icon_url = "https://i.imgur.com/H5OiNY3.jpg")
    embed.set_thumbnail(url="https://i.imgur.com/U2l3MiW.jpg")
    embed.add_field(name="ping", value="The basic testing function", inline=False)
    embed.add_field(name="rpic", value="Get a random picture", inline=False)
    embed.add_field(name="role_update", value="(Ad only) Department role update", inline=False)
    embed.add_field(name="m_check", value="(Ad only)(PC only) Get the member list of the guild", inline=False)
    embed.add_field(name="sqe", value="(Ad only) Event start function", inline=False)
    embed.add_field(name="eqe", value="(Ad only) Event end function", inline=False)
    embed.add_field(name="sb", value="Check scoreboard", inline=False)
    embed.add_field(name="p_m", value="(Ad only) Picture manipulation", inline=False)
    embed.add_field(name="p_check", value="(Ad only) Picture check", inline=False)
    embed.add_field(name="s_m", value="(Ad only) Scoreboard manipulation", inline=False)
    embed.add_field(name="cmd_list", value="Show SQCS Bot info", inline=False)
    embed.set_footer(text=now_time())
    await ctx.send(embed=embed)



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

bot.run(jdata['TOKEN'])