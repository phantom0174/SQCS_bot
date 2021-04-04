from pymongo import MongoClient
from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client, link, rsp
import core.functions as func
import discord
import asyncio
import random
import json
import core.score_module as sm


class Lecture(Cog_Extension):

    @commands.group()
    async def lect(self, ctx):
        pass

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][lect][list]')

        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find({})

        if data.count() == 0:
            await ctx.send(':exclamation: No data!')
            return

        lecture_list = str()
        for item in data:
            lecture_list += f'Name: {item["name"]}, Week: {item["_id"]}\n'

        await ctx.send(lecture_list)
        await ctx.send(':white_check_mark: Logging finished!')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def add(self, ctx, lect_week: int, lect_name: str):
        await func.report_cmd(self.bot, ctx,
                              f'[CMD EXECUTED][lect][add][lect_week: {lect_week}, lect_name: {lect_name}]')

        lecture_list_cursor = client["lecture_list"]

        # find if already exists
        data = lecture_list_cursor.find_one({"_id": lect_week})
        if data.count() != 0:
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
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][lect][remove][del_lect_week: {del_lect_week}]')

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
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][lect][start][week: {week}]')

        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find_one({"_id": week})

        if data.count() == 0:
            await ctx.send(f':exclamation: There exists no lecture on week {week}!')
            return

        if data["status"] == 1:
            await ctx.send(':exclamation: The lecture has already started!')
            return

        msg = '\n'.join(rsp["lecture"]["start"]["pt_1"]) + '\n'
        msg += f'星期 `{week}` 的講座 - `{data["name"]}` 開始了呦 \\^~^' + '\n'
        msg += '\n'.join(rsp["lecture"]["start"]["pt_2"])
        await ctx.send(msg)

        lecture_list_cursor.update({"_id": week}, {"$set": {"status": 1}})

        # delete previous special message
        msg_logs = await ctx.channel.history(limit=200).flatten()
        for msg in msg_logs:
            if len(msg.content) > 0 and msg.content[0] == '&':
                await msg.delete()

        # cd time from preventing member leave at once
        random.seed(func.now_time_info('hour') * 92384)
        await asyncio.sleep(random.randint(30, 180))

        channel_name = lecture_list_cursor.find_one({"_id": week})["name"]
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        attendants = list()
        for member in voice_channel.members:
            attendants.append(member.id)

        await func.report_lect_attend(self.bot, attendants, week)
        lecture_list_cursor.update_one({"_id": week}, {"$set": {"population": len(attendants)}})

    # lecture ans check
    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def ans_check(self, ctx, *, msg):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][lect][ans_check][correct_ans: {msg}]')

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

            if data.count() == 0:
                member_info = {
                    "_id": target_id,
                    "score": delta_score,
                    "count": 1
                }

                lecture_event_cursor.insert_one(member_info)
            else:
                lecture_event_cursor.update_one({"_id": target_id}, {"$inc": {"score": delta_score, "count": 1}})

            await sm.active_log_update(target_id)

            if top_score > 1:
                top_score -= 1

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def end(self, ctx, week: int):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][lect][emd][week: {week}]')

        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find_one({"_id": week})

        if data["status"] == 0:
            await ctx.send(':exclamation: The lecture has already ended!')
            return

        msg = '\n'.join(rsp["lecture"]["end"]["main"]) + '\n'
        population_level = int(round(data["population"] / 10))
        msg += rsp["lecture"]["end"]["reactions"][population_level]
        await ctx.send(msg)

        lecture_list_cursor.update_one({"_id": week}, {"$set": {"status": 0}})

        # adding scores and show lecture final data
        fl_client = MongoClient(link)["LightCube"]
        fl_cursor = fl_client["light-cube-info"]

        lecture_event_cursor = client["lecture_event"]
        data = lecture_event_cursor.find({}).sort("score", -1)

        if data.count() == 0:
            await ctx.send(':exclamation: There are no data to show!')
            return

        data_members = str()
        ranking = int(1)
        for member in data:
            if ranking == 1:
                medal = ':first_place:'
            elif ranking == 2:
                medal = ':second_place:'
            elif ranking == 3:
                medal = ':third_place:'
            else:
                medal = ':medal:'

            member_name = (await ctx.guild.fetch_member(member["_id"])).nick
            if member_name is None:
                member_name = (await ctx.guild.fetch_member[member["_id"]]).name

            data_members += f'{medal}{member_name}:: Score: {member["score"]}, Answer Count: {member["count"]}\n'

            fl_cursor.update_one({"_id": member["_id"]}, {"$inc": {"score": member["score"]}})
            await sm.active_log_update(member["_id"])

            ranking += 1

        await ctx.send(embed=func.create_embed(':scroll: Lecture Event Result', 'default', 0x42fcff, ['Lecture final info'], [data_members]))

        lecture_event_cursor.delete_many({})


def setup(bot):
    bot.add_cog(Lecture(bot))
