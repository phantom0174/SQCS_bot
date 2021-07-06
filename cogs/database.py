from discord.ext import commands
from core.cog_config import CogExtension
from core.db import link, fluctlight_client
from pymongo import MongoClient


class DataBase(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def db(self, ctx):
        pass

    @db.command()
    async def refresh_db(self, ctx):
        cursors = [
            fluctlight_client["MainFluctlights"],
            fluctlight_client["ViceFluctlights"]
        ]
        members_id = [member.id for member in ctx.guild.members]

        condition = {
            "_id": {
                "$nin": members_id
            }
        }
        for cursor in cursors:
            cursor.delete_many(condition)

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @db.command()
    async def copy(self, ctx, ori_db_name: str, ori_coll_name: str, target_db_name: str, target_coll_name: str):
        if ori_db_name == '' or ori_coll_name == '' or target_db_name == '' or target_coll_name == '':
            return await ctx.send(':x: 任何一個參數都不能為空字串！')

        # origin
        ori_db = MongoClient(link)[ori_db_name]
        ori_coll_cursor = ori_db[ori_coll_name]

        # target
        target_db = MongoClient(link)[target_db_name]
        target_coll_cursor = target_db[target_coll_name]

        ori_data = ori_coll_cursor.find({})
        for datum in ori_data:
            try:
                datum_dict = dict(datum)
                target_coll_cursor.insert_one(datum_dict)
            except:
                await ctx.send(f':x: 在複製id為 {datum["_id"]} 的檔案時發生了錯誤！')

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @db.command()
    async def move(self, ctx, ori_db_name: str, ori_coll_name: str, target_db_name: str, target_coll_name: str):
        if ori_db_name == '' or ori_coll_name == '' or target_db_name == '' or target_coll_name == '':
            return await ctx.send(':x: 任何一個參數都不能為空字串！')

        # origin
        ori_db = MongoClient(link)[ori_db_name]
        ori_coll_cursor = ori_db[ori_coll_name]

        # target
        target_db = MongoClient(link)[target_db_name]
        target_coll_cursor = target_db[target_coll_name]

        ori_data = ori_coll_cursor.find({})
        for datum in ori_data:
            try:
                datum_dict = dict(datum)
                target_coll_cursor.insert_one(datum_dict)
                ori_coll_cursor.delete_one({"_id": datum["_id"]})
            except:
                await ctx.send(f':x: 在轉移id為 {datum["_id"]} 的檔案時發生了錯誤！')

        await ctx.send(':white_check_mark: 指令執行完畢！')


def setup(bot):
    bot.add_cog(DataBase(bot))
