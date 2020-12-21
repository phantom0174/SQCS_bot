from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client, link
import functions as func
import discord
import asyncio
import random
import json


class Lecture(Cog_Extension):

    @commands.group()
    async def lect(self, ctx):
        pass

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        lecture_cursor = client["lecture_event"]
        data = lecture_cursor.find({})

        lecture_list = str()
        for item in data:
            lecture_list += f'Name: {item["name"]}, Week: {item["_id"]}\n'

        if data is None:
            lecture_list = 'No data.'

        await ctx.send(lecture_list)
        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - list used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def mani(self, ctx, *, msg):

        mode = msg.split(' ')[0]
        lecture_cursor = client["lecture_event"]

        if mode == '1':
            if len(msg.split(' ')) < 2:
                await ctx.send('Not enough parameters!')
                return

            lecture_name = msg.split(' ')[1]
            lecture_week = int(msg.split(' ')[2])

            lecture_info = {"_id": lecture_week, "name": lecture_name}
            lecture_cursor.insert_one(lecture_info)

            await ctx.send(f'Lecture {lecture_name}, on week {lecture_week} has been pushed!')
        elif mode == '0':
            delete_lecture_name = msg.split(' ')[1]

            try:
                lecture_cursor.delete_one({"name": delete_lecture_name})
                await ctx.send(f'Lecture {delete_lecture_name} has been removed!')
            except:
                await ctx.send(f'There are no lecture named {delete_lecture_name}!')
                return

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - mani used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def start(self, ctx, day: int):

        lecture_cursor =

        info.execute('SELECT STATUS FROM lecture_list WHERE Week=?;', (day))
        data = info.fetchall()[0]

        if data[0] == 1:
            await ctx.send(':exclamation: The lecture has already started!')
            return

        await ctx.send(':loudspeaker: @everyone，講座開始了！\n :bulb: 於回答講師問題時請在答案前方加上"&"，回答正確即可加分。')

        info.execute('UPDATE lecture_list SET Status=1 WHERE Week=?;', (day))

        def check(message):
            return message.channel == func.getChannel(self.bot, '_ToMV')

        await func.getChannel(self.bot, '_ToMV').send('request_score_weight')
        temp_weight = float((await self.bot.wait_for('message', check=check, timeout=30.0)).content)

        with open('jsons/lecture.json', mode='r', encoding='utf8') as temp_file:
            lect_data = json.load(temp_file)

        lect_data['temp_sw'] = temp_weight

        with open('jsons/lecture.json', mode='w', encoding='utf8') as temp_file:
            json.dump(lect_data, temp_file)

        msg_logs = await ctx.channel.history(limit=200).flatten()
        for msg in msg_logs:
            if len(msg.content) > 0 and msg.content[0] == '&':
                await msg.delete()

        # cd time from preventing member leave at once
        random.seed(func.now_time_info('hour') * 92384)
        await asyncio.sleep(random.randint(30, 180))

        # add score to the attendances
        info.execute('SELECT Name FROM lecture_list WHERE Week=?;', (day))
        channel_name = info.fetchall()[0][0]

        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        for member in voice_channel.members:
            await func.getChannel(self.bot, '_ToMV').send(f'lecture_attend {member.id}')

        info.connection.commit()
        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - start used by member {ctx.author.id}. {func.now_time_info("whole")}')

        # lecture ans check

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def ans_check(self, ctx, *, msg):
        CrtAns = msg.split(' ')
        msg_logs = await ctx.channel.history(limit=100).flatten()
        MemberCrtMsg = []  # correct message

        for log in msg_logs:
            if len(log.content) == 0:
                continue

            if (not log.author.bot) and log.content[0] == '&':
                await log.delete()
                for ans in CrtAns:
                    # correct answer is a subset of member answer
                    if log.content.find(ans) != -1:
                        MemberCrtMsg.append(log)
                        break

        MemberCrtMsg.reverse()

        # add score to correct members
        with open('jsons/lecture.json', mode='r', encoding='utf8') as temp_file:
            l_data = json.load(temp_file)  # lecture data

        TScore = float(5)
        for crt_msg in MemberCrtMsg:
            TargetId = crt_msg.author.id
            mScore = TScore * float(l_data["temp_sw"])
            info.execute('SELECT Id, Score, Count FROM lecture WHERE Id=?;', (TargetId))
            data = info.fetchall()

            if len(data) == 0:
                info.execute('INSERT INTO lecture VALUES(?, ?, 1);', (TargetId, mScore))
            else:
                old_Score = float(data[0][1])
                old_Count = int(data[0][2])

                info.execute('UPDATE lecture SET Score=?, Count=? WHERE Id=?;', (old_Score + mScore, old_Count + 1, TargetId))

            if TScore > 1:
                TScore -= 1

        info.connection.commit()

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - ans_check used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @lect.command()
    @commands.has_any_role('總召', 'Administrator')
    async def end(self, ctx, day: int):

        info.execute('SELECT Status FROM lecture_list WHERE Week=?;', (day))
        data = info.fetchall()[0]

        if data[0] == 0:
            await ctx.send(':exclamation: The lecture has already ended!')
            return

        await ctx.send(':loudspeaker: @here, 講座結束了!\n :partying_face: 感謝大家今天的參與!')

        info.execute('UPDATE lecture_list SET Status=0 WHERE Week=?;', (day))

        # adding scores and show lecture final data
        info.execute("SELECT * FROM lecture ORDER BY Score ASC")
        data = info.fetchall()
        if len(data) == 0:
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

            member_obj = await self.bot.guilds[0].fetch_member(member[0])  # member id
            data_members += f'{medal}{member_obj.nick}:: Score: {member[1]}, Answer Count: {member[2]}\n'
            await func.getChannel(self.bot, '_ToMV').send(f'lect_crt {member[0]} {member[1]}')
            ranking += 1

        await ctx.send(embed=func.create_embed(':scroll: Lecture Event Result', 0x42fcff, ['Lecture final info'], [data_members]))

        info.execute('DELETE FROM lecture')
        info.connection.commit()

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group lect - end used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Lecture(bot))
