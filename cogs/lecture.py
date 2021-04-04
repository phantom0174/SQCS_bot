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
        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find({})

        lecture_list = str()
        for item in data:
            lecture_list += f'Name: {item["name"]}, Week: {item["_id"]}\n'

        if data.count() == 0:
            lecture_list = 'No data.'

        await ctx.send(lecture_list)
        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - list used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def mani(self, ctx, *, msg):
        mode = msg.split(' ')[0]
        lecture_list_cursor = client["lecture_list"]

        if mode == '1':
            if len(msg.split(' ')) < 3:
                await ctx.send('Not enough parameters!')
                return

            lecture_name = msg.split(' ')[1]
            lecture_week = int(msg.split(' ')[2])

            lecture_info = {"_id": lecture_week, "name": lecture_name, "status": 0}
            lecture_list_cursor.insert_one(lecture_info)

            await ctx.send(f'Lecture {lecture_name}, on week {lecture_week} has been pushed!')
        elif mode == '0':
            delete_lecture_name = msg.split(' ')[1]

            try:
                lecture_list_cursor.delete_one({"name": delete_lecture_name})
                await ctx.send(f'Lecture {delete_lecture_name} has been removed!')
            except:
                await ctx.send(f'There are no lecture named {delete_lecture_name}!')
                return

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - mani used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def start(self, ctx, week: int):
        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find_one({"_id": week})

        if data["status"] == 1:
            await ctx.send(':exclamation: The lecture has already started!')
            return

        msg = '\n'.join(rsp["lecture"]["start"]["pt_1"]) + '\n'
        msg += f'星期 `{week}` 的講座 - `{data["name"]}` 開始了呦 \\^~^' + '\n'
        msg += '\n'.join(rsp["lecture"]["start"]["pt_2"])
        await ctx.send(msg)

        lecture_list_cursor.update({"_id": week}, {"$set": {"status": 1}})

        mvisualizer_client = MongoClient(link)['mvisualizer']
        score_cursor = mvisualizer_client["score_parameters"]

        score_weight = score_cursor.find_one({"_id": 0})["score_weight"]
        lect_attend_score = score_cursor.find_one({"_id": 0})["lecture_attend_point"]

        msg_logs = await ctx.channel.history(limit=200).flatten()
        for msg in msg_logs:
            if len(msg.content) > 0 and msg.content[0] == '&':
                await msg.delete()

        # cd time from preventing member leave at once
        random.seed(func.now_time_info('hour') * 92384)
        await asyncio.sleep(random.randint(30, 180))

        # add score to the attendances
        fl_client = MongoClient(link)["LightCube"]
        fl_cursor = fl_client["light-cube-info"]

        channel_name = lecture_list_cursor.find_one({"_id": week})["name"]
        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        for member in voice_channel.members:
            fl_cursor.update_one({"_id": member.id}, {"$inc": {"score": lect_attend_score * score_weight}})
            await sm.active_log_update(member.id)

        lecture_list_cursor.update_one({"_id": week}, {"$set": {"population": len(voice_channel.members)}})

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - start used by member {ctx.author.id}. {func.now_time_info("whole")}')

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
        mvisualizer_client = MongoClient(link)['mvisualizer']
        score_cursor = mvisualizer_client["score_parameters"]

        score_weight = score_cursor.find_one({"_id": 0})["score_weight"]

        top_score = float(5)
        for crt_msg in correct_msgs:
            TargetId = crt_msg.author.id
            delta_score = top_score * score_weight

            data = lecture_event_cursor.find_one({"_id": TargetId})

            if data.count() == 0:
                member_info = {"_id": TargetId, "score": delta_score, "count": 1}
                lecture_event_cursor.insert_one(member_info)
            else:
                lecture_event_cursor.update_one({"_id": TargetId}, {"$inc": {"score": delta_score, "count": 1}})

            await sm.active_log_update(TargetId)

            if top_score > 1:
                top_score -= 1

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - ans_check used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def end(self, ctx, week: int):

        lecture_list_cursor = client["lecture_list"]
        data = lecture_list_cursor.find_one({"_id": week})

        if data["status"] == 0:
            await ctx.send(':exclamation: The lecture has already ended!')
            return

        msg = '\n'.join(rsp["lecture"]["end"]["main"]) + '\n'
        population_level = int(data["population"] / 10)
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

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - end used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Lecture(bot))
