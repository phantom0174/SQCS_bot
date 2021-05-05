from discord.ext import commands
import random
from core.cog_config import CogExtension, JsonApi


class Picture(CogExtension):

    @commands.group()
    async def pic(self, ctx):
        pass

    @pic.command()
    async def add(self, ctx, link: str):

        pic_json = JsonApi().get_json('DynamicSetting')
        pic_json['picture_link'].append(link)
        JsonApi().put_json('DynamicSetting', pic_json)

        await ctx.send(f':white_check_mark: Object {link} successfully added!')

    @pic.command()
    async def remove(self, ctx, index: int):

        pic_json = JsonApi().get_json('DynamicSetting')

        if index >= int(len(pic_json['picture_link'])):
            return await ctx.send('Index out of range!')

        del_object = pic_json['picture_link'][index]
        del pic_json['picture_link'][index]

        JsonApi().put_json('DynamicSetting', pic_json)

        await ctx.send(f'Object {del_object} successfully deleted!')

    @pic.command()
    async def list(self, ctx):

        pic_json = JsonApi().get_json('DynamicSetting')

        pic_str = str()
        for i, pic in enumerate(pic_json['picture_link']):
            pic_str += f'{i}: {pic}\n'

            if len(pic_str) > 1600:
                await ctx.send(pic_str)

        if len(pic_str) > 0:
            await ctx.send(pic_str)

    @pic.command()
    async def random(self, ctx):

        pic_json = JsonApi().get_json('DynamicSetting')

        random_picture = random.choice(pic_json['picture_link'])
        await ctx.send(random_picture)


def setup(bot):
    bot.add_cog(Picture(bot))
