from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client
import core.functions as func
import discord
import random
import json


class Picture(Cog_Extension):

    @commands.group()
    async def pic(self, ctx):
        pass

    # picture_manipulation
    @pic.command()
    @commands.has_any_role('總召', 'Administrator')
    async def p_m(self, ctx, *, msg):

        if len(msg.split(' ')) > 2:
            await ctx.send('Too many arguments!')
            return

        if len(msg.split(' ')) == 1:
            await ctx.send('There are no selected target!')
            return

        await msg.delete()

        with open('jsons/setting.json', mode='r', encoding='utf8') as temp_file:
            setting_data = json.load(temp_file)

        mode = msg.split(' ')[0]
        m_object = msg.split(' ')[1]

        if mode == '0':
            if int(m_object) >= int(len(setting_data['pic'])):
                await ctx.send('Index out of range!')
                return

            del_object = setting_data['pic'][int(m_object)]
            del (setting_data['pic'][int(m_object)])
            await ctx.send(f'Object {del_object} successfully deleted!')
        elif mode == '1':
            setting_data['pic'].append(m_object)
            await ctx.send(f'Object {m_object} successfully added!')
        else:
            await ctx.send('Mode argument error!')

        with open('jsons/setting.json', mode='w', encoding='utf8') as temp_file:
            json.dump(setting_data, temp_file)

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group pic - p_m used by member {ctx.author.id}. {func.now_time_info("whole")}')

    # picture_check
    @pic.command()
    async def p_check(self, ctx):
        await ctx.message.delete()

        with open('jsons/setting.json', mode='r', encoding='utf8') as temp_file:
            setting_data = json.load(temp_file)

        pic_str = str()

        for i in range(len(setting_data['pic'])):
            pic_str += f'{i}: {setting_data["pic"][i]}\n'

        await ctx.send(pic_str)

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group pic - p_check used by member {ctx.author.id}. {func.now_time_info("whole")}')

    # random picture
    @pic.command()
    async def rpic(self, ctx):
        await ctx.message.delete()
        randPic = random.choice(jdata['pic'])
        await ctx.send(randPic)

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group pic - rpic used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Picture(bot))
