from discord.ext import commands, tasks
import asyncio
import random
from ...core import sqcs_module as sm
from ...core.db.jsonstorage import JsonApi
from ...core.db.mongodb import Mongo
from ...core.utils import Time, DiscordExt
from ...core.cog_config import CogExtension
from ...core.fluctlight_ext import Fluct
import discord
import statistics
from cn2an import an2cn


class LectureConfig(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def lect_config(self, ctx):
        pass

    @lect_config.command()
    async def list(self, ctx):
        """cmd
        列出所有有註冊的講座。
        """
        lect_set_cursor = Mongo('sqcs-bot').get_cur('LectureSetting')
        data = lect_set_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':exclamation: 沒有講座資料！')

        # improved code
        lecture_list = '\n'.join(map(
            lambda item: f'name: {item["name"]}\n'
                         f'week: {item["week"]}\n'
                         f'status: {item["status"]}\n'
                         f'population: {item["population"]}\n',
            data
        ))

        await ctx.send(lecture_list)
        await ctx.send(':white_check_mark: 紀錄尋找完畢！')

    @lect_config.command()
    async def add(self, ctx):
        """cmd
        註冊講座資料。
        """
        # ask for arguments
        def check(message):
            return message.channel == ctx.channel and message.author == ctx.author

        try:
            await ctx.send(':question: 請問講座名稱是什麼呢？')
            name = (await self.bot.wait_for('message', check=check, timeout=30)).content

            await ctx.send(':question: 請問在星期幾舉辦呢？')
            week = (await self.bot.wait_for('message', check=check, timeout=30)).content

            await ctx.send(':question: 請問在當天甚麼時候開始呢？')
            start_time = (await self.bot.wait_for('message', check=check, timeout=30)).content
        except asyncio.TimeoutError:
            return

        # left _id for random
        lecture_config = {
            "name": name,
            "week": int(week),
            "status": False,
            "population": []
        }
        lect_set_cursor = Mongo('sqcs-bot').get_cur('LectureSetting')
        lect_set_cursor.insert_one(lecture_config)

        lect_category_channel = ctx.guild.get_channel(743517006040662127)
        lecture_text_channel = await ctx.guild.create_text_channel(
            name=name,
            category=lect_category_channel,
            topic=f'講座在星期{an2cn(week)}的 {start_time}，歡迎參加！'
        )
        await lecture_text_channel.send(
            f':white_check_mark: 本頻道為 講座 - {name} 的專用頻道\n'
            f'自動生成時間：{Time.get_info("whole")}'
        )

        await ctx.guild.create_voice_channel(
            name=name,
            category=lect_category_channel
        )

        await ctx.send(':white_check_mark: 講座資料 與 專屬頻道 已建置完畢，謝謝你的配合！')

    @lect_config.command()
    async def remove(self, ctx, del_lect_week: int):
        """cmd
        刪除講座資料。
        """
        lect_set_cursor = Mongo('sqcs-bot').get_cur('LectureSetting')

        try:
            lect_set_cursor.delete_one({"week": del_lect_week})
            await ctx.send(f':white_check_mark: 星期 `{del_lect_week}` 的講座資料已被移除！')
        except Exception as e:
            await ctx.send(f':x: 移除星期 `{del_lect_week}` 的講座資料時發生了錯誤！')
            await ctx.send(content=e, delete_after=5.0)


class Lecture(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def lect(self, ctx):
        pass

    @lect.command()
    async def start(self, ctx, week: int):
        """cmd
        開始講座。

        .week: 星期數
        """
        lect_set_cursor = Mongo('sqcs-bot').get_cur('LectureSetting')
        lect_config = lect_set_cursor.find_one({"week": week})

        text_channel = discord.utils.get(ctx.guild.text_channels, name=lect_config['name'])
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=lect_config['name'])

        if not lect_config:
            return await ctx.send(f':x: 星期 `{week}` 沒有講座！')

        if lect_config["status"]:
            return await ctx.send(':x: 講座已經開始了！')

        msg = await JsonApi.get_humanity('lecture/start/pt_1', '\n')
        msg += f'星期 `{week}` 的講座－`{lect_config["name"]}` 開始了呦 \\^~^\n'
        msg += await JsonApi.get_humanity('lecture/start/pt_2')
        await text_channel.send(msg)

        execute = {
            "$set": {
                "population": [],
                "status": True
            }
        }
        lect_set_cursor.update({"week": week}, execute)

        # join the voice channel to speak
        voice_client = await voice_channel.connect()
        audio_source = discord.FFmpegPCMAudio('./bot/assets/audio/lecture_starts.mp3')
        voice_client.play(audio_source)
        while voice_client.is_playing():
            await asyncio.sleep(1)
        voice_client.stop()
        await voice_client.disconnect()

        # delete previous special message
        msg_logs = await text_channel.history(limit=200).flatten()
        for msg in msg_logs:
            if msg.content and msg.content.startswith('&'):
                await msg.delete()

        # cool-down to exclude member who leave at once
        await asyncio.sleep(random.randint(30, 180))

        attendants = [member.id for member in voice_channel.members]
        await sm.report_lect_attend(self.bot, attendants, week)

        # continue fetching population statistics, waiting for display using dash and flask integration

    # origin: lecture ans check
    @lect.command()
    async def add_point(self, ctx, delta_value: float, members_id: commands.Greedy[int]):
        lect_ongoing_cursor = Mongo('sqcs-bot').get_cur('LectureOngoing')

        fluct_ext = Fluct(score_mode='custom')
        for member_id in members_id:
            final_delta_score = await fluct_ext.add_score(member_id, delta_value)
            await fluct_ext.active_log_update(member_id)

            member_lecture_statistics = lect_ongoing_cursor.find_one({"_id": member_id})
            if not member_lecture_statistics:
                member_info = {
                    "_id": member_id,
                    "score": final_delta_score,
                    "count": 1
                }
                lect_ongoing_cursor.insert_one(member_info)
            else:
                execute = {
                    "$inc": {
                        "score": final_delta_score,
                        "count": 1
                    }
                }
                lect_ongoing_cursor.update_one({"_id": member_id}, execute)

        await ctx.send(':white_check_mark: 指令執行完畢！')

    @lect.command()
    async def end(self, ctx, week: int):
        """cmd
        結束講座。

        .week: 星期數
        """
        lect_set_cursor = Mongo('sqcs-bot').get_cur('LectureSetting')
        lect_config = lect_set_cursor.find_one({"week": week})

        text_channel = discord.utils.get(ctx.guild.text_channels, name=lect_config['name'])
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=lect_config['name'])

        if not lect_set_cursor["status"]:
            return await ctx.send(':exclamation: 講座已經結束了！')

        msg = await JsonApi.get_humanity('lecture/end/main', '\n')

        population_list = [pop['count'] for pop in lect_config["population"]]
        average_population = statistics.mean(population_list)

        population_level = int(round(average_population / 10))
        msg += await JsonApi.get_humanity(f'lecture/end/reactions/{population_level}')
        await text_channel.send(msg)
        execute = {
            "$set": {
                "status": False
            }
        }
        lect_set_cursor.update_one({"week": week}, execute)

        # join the voice channel to speak
        voice_client = await voice_channel.connect()
        audio_source = discord.FFmpegPCMAudio('./bot/assets/audio/lecture_ends.mp3')
        voice_client.play(audio_source)
        while voice_client.is_playing():
            await asyncio.sleep(1)
        voice_client.stop()
        await voice_client.disconnect()

        # show lecture final data
        lect_ongoing_cursor = Mongo('sqcs-bot').get_cur('LectureOngoing')
        answered_member_list = lect_ongoing_cursor.find({}).sort("score", -1)

        if answered_member_list.count() == 0:
            return await ctx.send(':exclamation: There are no data to show!')

        ranking_medal_prefix = {
            0: ':first_place:',
            1: ':second_place:',
            2: ':third_place:'
        }

        member_rank_list = ''
        for rank, member in enumerate(answered_member_list):
            medal = ranking_medal_prefix.get(rank, ':medal:')
            member_name = await DiscordExt.get_member_nick_name(ctx.guild, member["_id"])

            member_rank_list += (
                f'{medal}{member_name} | '
                f'Score: {member["score"]}, '
                f'Answer Count: {member["count"]}\n'
            )

        embed_para = [
            ':scroll: Lecture Event Result',
            'default',
            0x42fcff,
            ['Lecture final info'],
            [member_rank_list]
        ]
        await text_channel.send(embed=await DiscordExt.create_embed(*embed_para))
        lect_ongoing_cursor.delete_many({})

        # kick member from the voice channel
        countdown_duration = 60

        def content(s):
            return f':exclamation: 所有成員將在 {s} 秒後被移出 {voice_channel.name}'

        message = await ctx.send(content(countdown_duration))
        while countdown_duration:
            await message.edit(content=content(countdown_duration))
            await asyncio.sleep(1)
            countdown_duration -= 1

        await message.delete()

        for member in voice_channel.members:
            await member.move_to(None)


class LectureAttendVerify(CogExtension):
    @commands.group()
    async def lect_verify(self, ctx):
        pass

    @lect_verify.command()
    @commands.dm_only()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def attend(self, ctx, token: str):
        """cmd
        尚未啟用。
        """
        verify_cursor = Mongo('sqcs-bot').get_cur('Verification')
        data = verify_cursor.find_one({"TOKEN": token, "reason": "lect"})

        if not data:
            return await ctx.send(
                ':x: 講座資料庫中不存在這個token\n'
                '請在15秒後重試或聯絡總召'
            )

        # fetching score parameters
        fluct_ext = Fluct(member_id=ctx.author.id, score_mode='lect_attend')
        try:
            await fluct_ext.add_score()
            await fluct_ext.active_log_update()
            await fluct_ext.lect_attend_update()

            verify_cursor.delete_one({"TOKEN": token, "reason": "lect"})
            await ctx.send(':white_check_mark: 操作成功！')
        except BaseException:
            guild = self.bot.get_guild(784607509629239316)
            report_channel = discord.utils.get(guild.text_channels, name='sqcs-lecture-attend')

            await report_channel.send(
                f'[DB MANI ERROR][to: {ctx.author.id}][inc_score_mode: lecture_attend]'
            )
            await ctx.send(':x: 操作失敗，請聯繫總召><')


class LectureAuto(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lect_set_cursor = Mongo('sqcs-bot').get_cur('LectureSetting')
        self.lect_population_log.start()

    @tasks.loop(minutes=2)
    async def lect_population_log(self):
        await self.bot.wait_until_ready()

        ongoing_lect = self.lect_set_cursor.find_one({"status": True})
        if not ongoing_lect:
            return

        guild = self.bot.get_guild(743507979369709639)
        voice_channel = discord.utils.get(guild.voice_channels, name=ongoing_lect['name'])

        population = len(voice_channel.members)
        if population:
            execute = {
                "$push": {
                    "population": {
                        "count": population,
                        "time_stamp": Time.get_info('custom', "%Y-%m-%d %H:%M")
                    }
                }
            }
            self.lect_set_cursor.update_one({"week": ongoing_lect['week']}, execute)


def setup(bot):
    bot.add_cog(LectureConfig(bot))
    bot.add_cog(Lecture(bot))
    bot.add_cog(LectureAttendVerify(bot))
