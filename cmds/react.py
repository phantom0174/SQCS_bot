import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json
import random

with open("setting.json", mode='r', encoding='utf8') as jfile:
    jdata = json.load(jfile)

class React(Cog_Extension):


    @commands.command()
    async def rpic(ctx):
        randPic = random.choice(jdata['pic'])
        pic = discord.File(randPic)
        await ctx.send(file=pic)