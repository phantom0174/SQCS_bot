#D:\\Coding\\Github\\SQCS_bot\\bot.py
import discord
from discord.ext import commands
import json
import random
from datetime import datetime,timezone,timedelta

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

@bot.command()
async def ping(ctx):
    await ctx.send(f'{round(bot.latency * 1000)} (ms)')

@bot.command()
async def rpic(ctx):
    randPic = random.choice(jdata['pic'])
    pic = discord.File(randPic)
    await ctx.send(file=pic)

@bot.command()
async def role_update(ctx, msg):
    #'Mode:: 1:副召, 2:美宣, 3:網管, 4:公關, 5:議程, 6:管理'
    mode = int(msg.split(' ')[0])
    print(mode)
    msg_split = msg.split(' ')[1].split('\n')
    print(msg_split)
    school = []
    name = []

    if(int(len(msg_split))%2 == 0):
        if (mode == 1):
            new_role = ctx.guild.get_role(int(jdata['VC']))
        elif (mode == 2):
            new_role = ctx.guild.get_role(int(jdata['ADD']))
        elif (mode == 3):
            new_role = ctx.guild.get_role(int(jdata['NMD']))
        elif (mode == 4):
            new_role = ctx.guild.get_role(int(jdata['PRD']))
        elif (mode == 5):
            new_role = ctx.guild.get_role(int(jdata['MAD']))
        elif (mode == 6):
            new_role = ctx.guild.get_role(int(jdata['SAD']))


        for i in range(int(len(msg_split))):
            if(i+1 <= int(len(msg_split)/2)):
                school.append(msg_split[i])
            else:
                name.append(msg_split[i])

        for i in range(int(len(msg_split)/2)):
            for member in ctx.guild.members:
                member_tag = member.name.split(' ')
                print(member_tag)

                if(len(member_tag) >= 3):
                    member_school = member_tag[0]
                    member_name = member_tag[1]
                    if(member_school.find(school[i]) != -1  and member_name == name[i]):
                        old_role = member.top_role
                        if(len(member.roles) == 2):
                            await member.remove_roles(old_role)
                        await member.add_roles(new_role)
                        await ctx.channel.send(f'{member.name}\'s role was updated to {new_role}!')

        await ctx.send('Role update complete!')

    else:
        await ctx.send('School - Name length error!')

@bot.command()
async def sqe(ctx, msg):
    role_bool = int(0)
    for role in ctx.author.roles:
        if(str(role) == '總召'):
            role_bool = int(1)

    if(role_bool == int(0)):
        return

    temp_file = open('quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()
    print(quiz_data)

    quiz_data['event_status'] = "True"
    quiz_data['correct_ans'] = str(msg)

    await ctx.channel.send(f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
    channel = discord.utils.get(ctx.guild.text_channels, name='懸賞區')
    await channel.send('@here, a new term of quiz has started!\n Please make sure that your answer format is in spoiler form!\n (Put \"||\") at both front and back of your answer.)')
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)

    print(quiz_data)
    temp_file = open('quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


@bot.command()
async def eqe(ctx):
    role_bool = int(0)
    for role in ctx.author.roles:
        if (str(role) == '總召'):
            role_bool = int(1)

    if (role_bool == int(0)):
        return

    temp_file = open('quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()
    print(quiz_data)

    quiz_data['event_status'] = "False"
    quiz_data['correct_ans'] = "N/A"


    #await ctx.send(f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
    channel = discord.utils.get(ctx.guild.text_channels, name='懸賞區')
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)

    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

    await ctx.send(f'Quiz Event finished at time {dt2.strftime("%Y-%m-%d %H:%M:%S")}')

    winners = str()
    for winner in quiz_data["correct_ans_member"]:
        user = await bot.fetch_user(int(winner))
        winners += user.display_name
        winners += '\n'

    if(winners == ''):
        winners += 'none'

    quiz_data['answered_member'].clear()


    embed = discord.Embed(title="Quiz Event Result", color=0x42fcff)
    embed.set_thumbnail(url="https://i.imgur.com/26skltl.png")
    embed.add_field(name="Winner", value=winners, inline=False)
    embed.set_footer(text=str(dt2.strftime("%Y-%m-%d %H:%M:%S")))
    await ctx.send(embed=embed)

    #adding scores to score.json
    stemp_file = open('score.json', mode='r', encoding='utf8')
    score_data = json.load(stemp_file)
    stemp_file.close()
    print(score_data)

    for correct_member in quiz_data['correct_ans_member']:
        user_log = int(0)
        for i in range(len(score_data['member_id'])):
            if(score_data['member_id'][i] == str(correct_member)):
                score_data['member_score'][i] = str(int(score_data['member_score'][i]) + 1)
                user_log = int(1)
                break

        if(user_log == int(0)):
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

@bot.listen()
async def on_message(msg):
    if(msg.author == bot.user or msg.content[0] == '+' or msg.content[0] == '~'):
        return

    await msg.delete()
    temp_file = open('quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()
    print(quiz_data)

    if(quiz_data["event_status"] == 'False'):
        return

    print(msg.content[0:2], msg.content[-2:], msg.content[2:-2])
    if(msg.content[0:2] == '||' and msg.content[-2:] == '||' and msg.channel.id == 746014424086610012):
        answered = int(0)
        for answered_member_id in quiz_data['answered_member']:
            if(str(msg.author.id) == answered_member_id):
                await msg.channel.send(f'{msg.author.mention}, I\'ve already got your answer!')
                answered = int(1)
                break

        if(answered == int(0)):
            await msg.channel.send(f'{msg.author.mention}, I got your answer!')
            if(msg.content[2:-2] == quiz_data["correct_ans"]):
                quiz_data["correct_ans_member"].append(str(msg.author.id))
                quiz_data["answered_member"].append(str(msg.author.id))
    else:
        await msg.channel.send(f'{msg.author.mention}, your answer has a wrong format!')

    print(quiz_data)
    temp_file = open('quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


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