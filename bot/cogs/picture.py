from discord.ext import commands
import random
from ..core.cog_config import CogExtension
from ..core.db.jsonstorage import JsonApi


class Picture(CogExtension):

    @commands.group()
    async def pic(self, ctx):
        pass

    @pic.command()
    async def list(self, ctx):
        """cmd
        查詢資料庫中所有的圖片。
        """
        pic_json = JsonApi.get('DynamicSetting')

        pic_str = ''
        for i, pic in enumerate(pic_json['picture_link']):
            pic_str += f'{i}: {pic}\n'

            if len(pic_str) > 1600:
                await ctx.send(pic_str)

        if len(pic_str) > 0:
            await ctx.send(pic_str)

    @pic.command(aliases=['insert'])
    async def add(self, ctx, link: str):
        """cmd
        將一張圖片加入到資料庫中。

        .link: 圖片的超連結
        """
        pic_json = JsonApi.get('DynamicSetting')
        pic_json['picture_link'].append(link)
        JsonApi.put('DynamicSetting', pic_json)

        await ctx.send(f':white_check_mark: 圖片 {link} 已新增！')

    @pic.command(aliases=['delete'])
    async def remove(self, ctx, index: int):
        """cmd
        將一張圖片從資料庫中移除。

        .index: 圖片的位置（可利用list進行查詢）
        """
        pic_json = JsonApi.get('DynamicSetting')

        storage_size = len(pic_json['picture_link'])
        if index >= storage_size:
            return await ctx.send(
                f':x: 位置的數字要介於 [0 ~ {storage_size - 1}] 之間！\n'
            )

        del_object = pic_json['picture_link'][index]
        del pic_json['picture_link'][index]

        JsonApi.put('DynamicSetting', pic_json)

        await ctx.send(f':white_check_mark: 圖片 {del_object} 已刪除！')

    @pic.command(aliases=['get'])
    async def random(self, ctx):
        """cmd
        發送一張隨機的圖片。
        """
        pic_json = JsonApi.get('DynamicSetting')
        random_picture = random.choice(pic_json['picture_link'])
        await ctx.send(random_picture)


def setup(bot):
    bot.add_cog(Picture(bot))
