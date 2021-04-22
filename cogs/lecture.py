from discord.ext import commands
import discord
import asyncio
import random
import core.score_module as sm
from core.setup import client, rsp, fluctlight_client
import core.functions as func
from core.classes import CogExtension


class Lecture(CogExtension):

    @commands.group()
    async def lect(self, ctx):
        pass

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):

        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find({})

        if data.count() == 0:
            await ctx.send(':exclamation: No data!')
            return

        # improved code
        lecture_list = '\n'.join(
            map(lambda item: f'Name: {item["name"]}, Week: {item["_id"]}', data)
        )

        await ctx.send(lecture_list)
        await ctx.send(':white_check_mark: Logging finished!')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def add(self, ctx, lect_week: int, lect_name: str):

        lecture_list_cursor = client["lecture_list"]

        # find if already exists
        data = lecture_list_cursor.find_one({"_id": lect_week})
        if data:
            await ctx.send('There already exists a lecture on the same day!')
            return

        lecture_info = {
            "_id": lect_week,
            "name": lect_name,
            "status": 0
        }

        lecture_list_cursor.insert_one(lecture_info)

        await ctx.send(f'Lecture {lect_name}, on week {lect_week} has been added!')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remove(self, ctx, del_lect_week: int):

        lecture_list_cursor = client["lecture_list"]

        try:
            lecture_list_cursor.delete_one({"week": del_lect_week})
            await ctx.send(f':white_check_mark: The lecture on week `{del_lect_week}` has been removed!')
        except Exception as e:
            await ctx.send(f':exclamation: Error occurred when deleting lecture on week {del_lect_week}!')
            await ctx.send(content=e, delete_after=5.0)

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def start(self, ctx, week: int):

        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find_one({"_id": week})

        if not data:
            await ctx.send(f':exclamation: There exists no lecture on week {week}!')
            return

        if data["status"] == 1:
            await ctx.send(':exclamation: The lecture has already started!')
            return

        msg = '\n'.join(rsp["lecture"]["start"]["pt_1"]) + '\n'
        msg += f'星期 `{week}` 的講座 - `{data["name"]}` 開始了呦 \\^~^' + '\n'
        msg += '\n'.join(rsp["lecture"]["start"]["pt_2"])
        await ctx.send(msg)

        execute = {
            "$set": {
                "status": 1
            }
        }

        lecture_list_cursor.update({"_id": week}, execute)

        # delete previous special message
        msg_logs = await ctx.channel.history(limit=200).flatten()
        for msg in msg_logs:
            if len(msg.content) > 0 and msg.content[0] == '&':
                await msg.delete()

        # cd time from preventing member leave at once
        # need to fix for stable pattern
        random.seed(func.now_time_info('hour') * 92384)
        await asyncio.sleep(random.randint(30, 180))

        channel_name = lecture_list_cursor.find_one({"_id": week})["name"]
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        attendants = [member.id for member in voice_channel.members]

        await func.report_lect_attend(self.bot, attendants, week)
        execute = {
            "$set": {
                "population": len(attendants)
            }
        }
        lecture_list_cursor.update_one({"_id": week}, execute)

    # lecture ans check
    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def ans_check(self, ctx, *, msg):

        correct_answer = msg.split(' ')
        msg_logs = await ctx.channel.history(limit=100).flatten()
        correct_msgs = []  # correct message

        for log in msg_logs:
            if len(log.content) == 0:
                continue

            if (not log.author.bot) and log.content[0] == '&':
                await log.delete()
                for ans in correct_answer:
                    # correct answer is a subset of member answer
                    if log.content.find(ans) != -1:
                        correct_msgs.append(log)
                        break

        correct_msgs.reverse()

        # add score to correct members
        lecture_event_cursor = client["lecture_event"]
        score_cursor = client["score_parameters"]

        score_weight = score_cursor.find_one({"_id": 0})["score_weight"]

        top_score = float(5)
        for crt_msg in correct_msgs:
            target_id = crt_msg.author.id
            delta_score = top_score * score_weight

            data = lecture_event_cursor.find_one({"_id": target_id})

            if not data:
                member_info = {
                    "_id": target_id,
                    "score": delta_score,
                    "count": 1
                }

                lecture_event_cursor.insert_one(member_info)
            else:
                execute = {
                    "$inc": {
                        "score": delta_score,
                        "count": 1
                    }
                }
                lecture_event_cursor.update_one({"_id": target_id}, execute)

            await sm.active_log_update(target_id)

            if top_score > 1:
                top_score -= 1

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def end(self, ctx, week: int):

        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find_one({"_id": week})

        if data["status"] == 0:
            await ctx.send(':exclamation: The lecture has already ended!')
            return

        msg = '\n'.join(rsp["lecture"]["end"]["main"]) + '\n'
        population_level = int(round(data["population"] / 10))
        msg += rsp["lecture"]["end"]["reactions"][population_level]
        await ctx.send(msg)
        execute = {
            "$set": {
                "status": 0
            }
        }
        lecture_list_cursor.update_one({"_id": week}, execute)

        # adding scores and show lecture final data
        fl_cursor = fluctlight_client["light-cube-info"]

        lecture_event_cursor = client["lecture_event"]
        data = lecture_event_cursor.find({}).sort("score", -1)

        if data.count() == 0:
            await ctx.send(':exclamation: There are no data to show!')
            return

        data_members = str()

        ranking_medal_prefix = {
            0: ':first_place:',
            1: ':second_place:',
            2: ':third_place:'
        }

        for rank, member in enumerate(data):
            medal = ranking_medal_prefix.get(rank, ':medal:')

            member_name = (await ctx.guild.fetch_member(member["_id"])).nick
            if member_name is None:
                member_name = (await ctx.guild.fetch_member[member["_id"]]).name

            data_members += f'{medal}{member_name}:: Score: {member["score"]}, Answer Count: {member["count"]}\n'

            execute = {
                "$inc": {
                    "score": member["score"]
                }
            }
            fl_cursor.update_one({"_id": member["_id"]}, execute)
            await sm.active_log_update(member["_id"])

        embed_para = [
            ':scroll: Lecture Event Result',
            'default',
            0x42fcff,
            ['Lecture final info'],
            [data_members]
        ]

        await ctx.send(embed=func.create_embed(*embed_para))

        lecture_event_cursor.delete_many({})

        # kick member from the voice channel
        countdown_duration = 60
        channel_name = lecture_list_cursor.find_one({"_id": week})["name"]
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        def content(s):
            return f':exclamation: 所有成員將在 {s} 秒後被移出 {voice_channel.name}'

        message = await ctx.send(content(countdown_duration))
        while countdown_duration > 0:
            await message.edit(content=content(countdown_duration))
            await asyncio.sleep(1)
            countdown_duration -= 1

        await message.delete()

        for member in voice_channel.members:
            await member.move_to(None)


def setup(bot):
    bot.add_cog(Lecture(bot))
