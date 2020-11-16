#D:\\Coding\\Github\\SQCS_bot\\bot.py
import discord
from discord.ext import commands
import json
import random

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
async def role_update(ctx, *, msg):
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