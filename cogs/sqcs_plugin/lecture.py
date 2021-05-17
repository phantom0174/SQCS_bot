from discord.ext import commands
import asyncio
import random
import core.sqcs_module as sm
from core.db import self_client, huma_get, fluctlight_client
from core.utils import DiscordExt
from core.cog_config import CogExtension
from core.fluctlight_ext import Fluct


class Lecture(CogExtension):

    @commands.group()
    async def lect(self, ctx):
        pass

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        lect_set_cursor = self_client["LectureSetting"]
        data = lect_set_cursor.find({})

        if data.count() == 0:
            return await ctx.send(':exclamation: 沒有講座資料！')

        # improved code
        lecture_list = '\n'.join(map(
                lambda item: f'name: {item["name"]}\n'
                             f'week: {item["week"]}\n'
                             f'status: {item["status"]}\n'
                             f'population: {item["population"]}\n'
                             f'text_id: {item["text_id"]}\n'
                             f'voice_id: {item["voice_id"]}\n',
                data
        ))

        await ctx.send(lecture_list)
        await ctx.send(':white_check_mark: 紀錄尋找完畢！')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def add(self, ctx):
        # ask for arguments
        def check(message):
            return message.channel == ctx.channel and message.author == ctx.author

        try:
            await ctx.send(':question: 請問講座名稱是什麼呢？')
            name = (await self.bot.wait_for('message', check=check, timeout=30)).content

            await ctx.send(':question: 請問在星期幾舉辦呢？')
            week = (await self.bot.wait_for('message', check=check, timeout=30)).content

            await ctx.send(':question: 請問使用的文字頻道id為多少呢？')
            text_channel_id = (await self.bot.wait_for('message', check=check, timeout=30)).content

            await ctx.send(':question: 請問使用的語音頻道id為多少呢？')
            voice_channel_id = (await self.bot.wait_for('message', check=check, timeout=30)).content
        except asyncio.TimeoutError:
            return

        # left _id for random
        lecture_config = {
            "name": name,
            "week": int(week),
            "status": False,
            "population": 0,
            "text_id": int(text_channel_id),
            "voice_id": int(voice_channel_id)
        }
        lect_set_cursor = self_client["LectureSetting"]
        lect_set_cursor.insert_one(lecture_config)

        await ctx.send(':white_check_mark: 講座資料建檔完畢，謝謝你的配合！')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remove(self, ctx, del_lect_week: int):
        lect_set_cursor = self_client["LectureSetting"]

        try:
            lect_set_cursor.delete_one({"week": del_lect_week})
            await ctx.send(f':white_check_mark: 星期 `{del_lect_week}` 的講座資料已被移除！')
        except Exception as e:
            await ctx.send(f':x: 移除星期 `{del_lect_week}` 的講座資料時發生了錯誤！')
            await ctx.send(content=e, delete_after=5.0)

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def start(self, ctx, week: int):
        lect_set_cursor = self_client["LectureSetting"]
        lect_config = lect_set_cursor.find_one({"week": week})

        if not lect_config:
            return await ctx.send(f':x: 星期 `{week}` 沒有講座！')

        if lect_config["status"]:
            return await ctx.send(':x: 講座已經開始了！')

        msg = huma_get('lecture/start/pt_1', '\n')
        msg += f'星期 `{week}` 的講座－`{lect_config["name"]}` 開始了呦 \\^~^\n'
        msg += huma_get('lecture/start/pt_2')
        await ctx.send(msg)

        execute = {
            "$set": {
                "status": True
            }
        }
        lect_set_cursor.update({"week": week}, execute)

        # delete previous special message
        text_channel = self.bot.get_channel(lect_config["text_id"])
        msg_logs = await text_channel.history(limit=200).flatten()
        for msg in msg_logs:
            if msg.content and msg.content.startswith('&'):
                await msg.delete()

        # cool-down to exclude member who leave at once
        await asyncio.sleep(random.randint(30, 180))

        voice_channel = self.bot.get_channel(lect_config["voice_id"])
        attendants = [member.id for member in voice_channel.members]

        await sm.report_lect_attend(self.bot, attendants, week)
        execute = {
            "$set": {
                "population": len(attendants)
            }
        }
        lect_set_cursor.update_one({"week": week}, execute)

    # lecture ans check
    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def ans_check(self, ctx, *, msg):

        answer_alias = msg.split(' ')
        msg_logs = await ctx.channel.history(limit=100).flatten()
        correct_msgs = []  # correct message

        for log in msg_logs:
            if not log.content or log.author.bot or not log.content.startswith('&'):
                continue

            await log.delete()
            for ans in answer_alias:
                # correct answer is a subset of member answer
                if log.content.find(ans) != -1:
                    correct_msgs.append(log)
                    break

        correct_msgs.reverse()
        crt_member_id_list = [crt_msg.author.id for crt_msg in correct_msgs]

        # add score to correct members
        lect_ongoing_cursor = self_client["LectureOngoing"]
        score_cursor = self_client["ScoreSetting"]

        score_weight = score_cursor.find_one({"_id": 0})["score_weight"]

        top_score = float(5)
        for member_id in crt_member_id_list:
            delta_score = round(top_score * score_weight, 2)

            data = lect_ongoing_cursor.find_one({"_id": member_id})

            if not data:
                member_info = {
                    "_id": member_id,
                    "score": delta_score,
                    "count": 1
                }

                lect_ongoing_cursor.insert_one(member_info)
            else:
                execute = {
                    "$inc": {
                        "score": delta_score,
                        "count": 1
                    }
                }
                lect_ongoing_cursor.update_one({"_id": member_id}, execute)

            await Fluct().active_log_update(member_id)

            if top_score > 1:
                top_score -= 1

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def end(self, ctx, week: int):

        lect_set_cursor = self_client["LectureSetting"]
        lect_config = lect_set_cursor.find_one({"week": week})

        if not lect_set_cursor["status"]:
            return await ctx.send(':exclamation: 講座已經結束了！')

        msg = huma_get('lecture/end/main', '\n')
        population_level = int(round(lect_config["population"] / 10))
        msg += huma_get(f'lecture/end/reactions/{population_level}')
        await ctx.send(msg)
        execute = {
            "$set": {
                "status": False
            }
        }
        lect_set_cursor.update_one({"week": week}, execute)

        # adding scores and show lecture final data
        fl_cursor = fluctlight_client["MainFluctlights"]

        lect_ongoing_cursor = self_client["LectureOngoing"]
        answered_member_list = lect_ongoing_cursor.find({}).sort("score", -1)

        if answered_member_list.count() == 0:
            return await ctx.send(':exclamation: There are no data to show!')

        member_rank_list = str()

        ranking_medal_prefix = {
            0: ':first_place:',
            1: ':second_place:',
            2: ':third_place:'
        }

        for rank, member in enumerate(answered_member_list):
            medal = ranking_medal_prefix.get(rank, ':medal:')
            member_name = await DiscordExt.get_member_nick_name(ctx.guild, member["_id"])

            member_rank_list += (
                f'{medal}{member_name} | '
                f'Score: {member["score"]}, '
                f'Answer Count: {member["count"]}\n'
            )

            execute = {
                "$inc": {
                    "score": member["score"]
                }
            }
            fl_cursor.update_one({"_id": member["_id"]}, execute)
            await Fluct().active_log_update(member["_id"])

        embed_para = [
            ':scroll: Lecture Event Result',
            'default',
            0x42fcff,
            ['Lecture final info'],
            [member_rank_list]
        ]

        await ctx.send(embed=await DiscordExt.create_embed(*embed_para))

        lect_ongoing_cursor.delete_many({})

        # kick member from the voice channel
        countdown_duration = 60
        voice_channel = self.bot.get_channel(lect_config["voice_id"])

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


def setup(bot):
    bot.add_cog(Lecture(bot))
