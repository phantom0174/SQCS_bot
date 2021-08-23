from discord.ext import commands, tasks
from ..core.cog_config import CogExtension
from ..core.db.mongodb import Mongo, mongo_client
from ..core.db import storj
import pendulum as pend
from ..core.utils import Time
import os
import json
import bson


class DataBase(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def db(self, ctx):
        pass

    @db.command()
    async def refresh_db(self, ctx):
        """cmd
        重新整理搖光資料庫。
        """
        cursors = list(Mongo('LightCube').get_curs(['MainFluctlights', 'ViceFluctlights']))
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
        """cmd
        複製集合中的資料。
        """
        if '' in [ori_db_name, ori_coll_name, target_db_name, target_coll_name]:
            return await ctx.send(':x: 任何一個參數都不能為空字串！')

        # origin
        ori_coll_cursor = Mongo(ori_db_name).get_cur(ori_coll_name)

        # target
        target_coll_cursor = Mongo(target_db_name).get_cur(target_coll_name)

        ori_data = ori_coll_cursor.find({})
        for datum in ori_data:
            try:
                datum_dict = dict(datum)
                target_coll_cursor.insert_one(datum_dict)
            except BaseException:
                await ctx.send(f':x: 在複製id為 {datum["_id"]} 的檔案時發生了錯誤！')

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @db.command()
    async def move(self, ctx, ori_db_name: str, ori_coll_name: str, target_db_name: str, target_coll_name: str):
        """cmd
        移動集合中的資料。
        """
        if '' in [ori_db_name, ori_coll_name, target_db_name, target_coll_name]:
            return await ctx.send(':x: 任何一個參數都不能為空字串！')

        # origin
        ori_coll_cursor = Mongo(ori_db_name).get_cur(ori_coll_name)

        # target
        target_coll_cursor = Mongo(target_db_name).get_cur(target_coll_name)

        ori_data = ori_coll_cursor.find({})
        for datum in ori_data:
            try:
                datum_dict = dict(datum)
                target_coll_cursor.insert_one(datum_dict)
                ori_coll_cursor.delete_one({"_id": datum["_id"]})
            except BaseException:
                await ctx.send(f':x: 在轉移id為 {datum["_id"]} 的檔案時發生了錯誤！')

        await ctx.send(':white_check_mark: 指令執行完畢！')


class MongoDBBackup(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bucket = 'mongodbbackup'

        self.backup.start()
        self.delete_outdated.start()

    @tasks.loop(minutes=20)
    async def backup(self):
        await self.bot.wait_until_ready()

        time_now = pend.now('Asia/Taipei')
        time_tomorrow = pend.tomorrow('Asia/Taipei')

        # backup at time 23:00 ~ 24:00
        if (time_tomorrow - time_now).in_minutes() > 60:
            return

        today = Time.get_info('main')

        search_options = {
            "prefix": f"{today}/",
            "recursive": True,
            "system": False
        }
        result = await storj.list_file(
            bucket_name=self.bucket,
            options=search_options
        )

        # database has been backuped
        if result:
            return

        dbs = mongo_client.list_database_names()
        dbs = [item for item in dbs if item not in ['admin', 'local']]

        for db_name in dbs:
            db = mongo_client[db_name]
            for coll in db.list_collection_names():

                cursor = db[coll]
                coll_data = cursor.find({})

                if not coll_data:
                    continue

                def remake_id(obj: dict):
                    if isinstance(obj["_id"], bson.objectid.ObjectId):
                        obj["_id"] = str(obj["_id"])
                    return obj

                coll_to_json = [remake_id(item) for item in list(coll_data)]

                coll_to_json = json.dumps(
                    coll_to_json,
                    ensure_ascii=False,
                    indent=4
                )
                with open(f'./bot/buffer/{coll}.json', 'w', encoding='utf8') as buffer:
                    buffer.write(coll_to_json)

                await storj.upload_file(
                    bucket_name=self.bucket,
                    local_path=f'./bot/buffer/{coll}.json',
                    storj_path=f'{today}/{db_name}/{coll}.json'
                )

                try:
                    os.remove(f'./bot/buffer/{coll}.json')
                except BaseException:
                    pass

    @tasks.loop(hours=2)
    async def delete_outdated(self):
        await self.bot.wait_until_ready()

        time_now = pend.now('Asia/Taipei')

        search_options = {
            "prefix": '',
            "recursive": False,
            "system": False
        }
        storj_root_folders = await storj.list_file(
            bucket_name=self.bucket,
            options=search_options
        )

        for folder_name in storj_root_folders:
            # "name/" -> "name"
            time_folder_create = pend.parse(folder_name[:-1], tz='Asia/Taipei')

            if (time_folder_create - time_now).in_days() > 14:
                await storj.delete_folder(
                    bucket_name=self.bucket,
                    storj_path=folder_name
                )


def setup(bot):
    bot.add_cog(DataBase(bot))
    bot.add_cog(MongoDBBackup(bot))
