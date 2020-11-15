import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='+')

@bot.event
async def on_ready():
    print(">> Bot is online <<")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(774794670034124850)
    await channel.send(f'{member} join!')


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(774794670034124850)
    await channel.send(f'{member} leave!')

@bot.command()
async def ping(ctx):
    await ctx.send(f'{round(bot.latency*1000)} (ms)')


bot.run("NzQ3NDU3Mzg2NDEwODAzMjEw.X0PJ8A.jrL7Edp_Stl17AHy1DiLpw2_khM")