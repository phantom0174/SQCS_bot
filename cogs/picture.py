from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata
import core.functions as func
import random
import json


class Picture(Cog_Extension):

    @commands.group()
    async def pic(self, ctx):
        pass

    @pic.command()
    @commands.has_any_role('總召', 'Administrator')
    async def add(self, ctx, link: str):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][pic][add][link: {link}]')

        with open('jsons/setting.json', mode='r', encoding='utf8') as temp_file:
            setting_data = json.load(temp_file)

        setting_data['pic'].append(link)

        with open('jsons/setting.json', mode='w', encoding='utf8') as temp_file:
            json.dump(setting_data, temp_file)

        await ctx.send(f':white_check_mark: Object {link} successfully added!')

    @pic.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remove(self, ctx, index: int):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][pic][remove][index: {index}]')

        with open('jsons/setting.json', mode='r', encoding='utf8') as temp_file:
            setting_data = json.load(temp_file)

        if index >= int(len(setting_data['pic'])):
            await ctx.send('Index out of range!')
            return

        del_object = setting_data['pic'][index]
        del(setting_data['pic'][index])

        with open('jsons/setting.json', mode='w', encoding='utf8') as temp_file:
            json.dump(setting_data, temp_file)

        await ctx.send(f'Object {del_object} successfully deleted!')

    @pic.command()
    async def list(self, ctx):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][pic][link]')

        with open('jsons/setting.json', mode='r', encoding='utf8') as temp_file:
            setting_data = json.load(temp_file)

        pic_str = str()
        for i, pic in enumerate(setting_data['pic']):
            pic_str += f'{i}: {setting_data["pic"][i]}\n'

            if len(pic_str) > 1600:
                await ctx.send(pic_str)

        if len(pic_str) > 0:
            await ctx.send(pic_str)

    @pic.command()
    async def random(self, ctx):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][pic][random]')

        random_picture = random.choice(jdata['pic'])
        await ctx.send(random_picture)


def setup(bot):
    bot.add_cog(Picture(bot))
