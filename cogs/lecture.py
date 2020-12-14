from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import *
from functions import *
import discord
import asyncio
import random


class Lecture(Cog_Extension):

    @commands.group()
    async def lect(self, ctx):
        pass

    @lect.command()
    async def list(self, ctx):
        info.execute('SELECT * FROM lecture_list;')
        data = info.fetchall()

        lect_list = str()
        for lect_info in data:
            lect_list += f'Name: {lect_info[0]}, Week: {lect_info[1]}\n'

        if lect_list == '':
            lect_list = 'No data.'

        await ctx.send(lect_list)
        await getChannel('_Report').send(
            f'[Command]Group lect - list used by member {ctx.author.id}. {now_time_info("whole")}')

    @lect.command()
    async def mani(self, ctx, *, msg):

        if not role_check(ctx.author.roles, ['總召', 'Administrator']):
            await ctx.send(':no_entry_sign: You can\'t use that command!')
            return

        mode = msg.split(' ')[0]
        if mode == '1':
            if len(msg.split(' ')) < 2:
                await ctx.send('Not enough parameters!')
                return

            lect_name = msg.split(' ')[1]
            lect_week = msg.split(' ')[2]
            info.execute(f'INSERT INTO lecture_list VALUES("{lect_name}", {lect_week}, 0);')
            await ctx.send(f'Lecture {lect_name}, on week {lect_week} has been pushed!')
        elif mode == '0':
            delete_lect = msg.split(' ')[1]

            try:
                info.execute(f'DELETE FROM lecture_list WHERE Name={delete_lect};')
                await ctx.send(f'Lecture {delete_lect} has been removed!')
            except:
                await ctx.send(f'There are no lecture named {delete_lect}!')
                return

        info.connection.commit()
        await getChannel('_Report').send(
            f'[Command]Group lect - mani used by member {ctx.author.id}. {now_time_info("whole")}')

    @lect.command()
    async def start(self, ctx, day: int):
        if not role_check(ctx.author.roles, ['總召', 'Administrator']):
            await ctx.send(':no_entry_sign: You can\'t use that command!')
            return

        info.execute(f'SELECT STATUS FROM lecture_list WHERE Week={day};')
        data = info.fetchall()[0]

        if data[0] == 1:
            await ctx.send(':exclamation: The lecture has already started!')
            return

        await ctx.send(':loudspeaker: @everyone，講座開始了！\n :bulb: 於回答講師問題時請在答案前方加上"&"，回答正確即可加分。')

        info.execute(f'UPDATE lecture_list SET Status=1 WHERE Week={day};')

        def check(message):
            return message.channel == getChannel('_ToMV')

        await getChannel('_ToMV').send('request_score_weight')
        temp_weight = float((await self.bot.wait_for('message', check=check, timeout=30.0)).content)

        temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
        lect_data = json.load(temp_file)
        temp_file.close()

        lect_data['temp_sw'] = temp_weight

        temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
        json.dump(lect_data, temp_file)
        temp_file.close()

        msg_logs = await ctx.channel.history(limit=200).flatten()
        for msg in msg_logs:
            if len(msg.content) > 0 and msg.content[0] == '&':
                await msg.delete()

        # cd time from preventing member leave at once
        random.seed(now_time_info('hour') * 92384)
        await asyncio.sleep(random.randint(30, 180))

        # add score to the attendances
        info.execute(f'SELECT Name FROM lecture_list WHERE Week={day};')
        channel_name = info.fetchall()[0][0]

        voice_channel = discord.utils.get(ctx.guild.voice_channels, name=channel_name)

        for member in voice_channel.members:
            await getChannel('_ToMV').send(f'lecture_attend {member.id}')

        info.connection.commit()
        await getChannel('_Report').send(
            f'[Command]Group lect - start used by member {ctx.author.id}. {now_time_info("whole")}')

        # lecture ans check

    @lect.command()
    async def ans_check(self, ctx, *, msg):
        CrtAns = msg.split(' ')
        msg_logs = await ctx.channel.history(limit=100).flatten()
        MemberCrtMsg = []  # correct message

        for msg in msg_logs:
            if len(msg.content) == 0:
                continue

            if (not msg.author.bot) and msg.content[0] == '&':
                await msg.delete()
                for ans in CrtAns:
                    # correct answer is a subset of member answer
                    if msg.content.find(ans) != -1:
                        MemberCrtMsg.append(msg)
                        break

        MemberCrtMsg.reverse()

        # add score to correct members
        temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
        l_data = json.load(temp_file)  # lecture data
        temp_file.close()

        TScore = float(5)
        for crt_msg in MemberCrtMsg:
            TargetId = crt_msg.author.id
            mScore = TScore * float(l_data["temp_sw"])
            info.execute(f'SELECT Id, Score, Count FROM lecture WHERE Id={TargetId}')
            data = info.fetchall()

            if len(data) == 0:
                info.execute(f'INSERT INTO lecture VALUES({TargetId}, {mScore}, 1);')
            else:
                old_Score = float(data[0][1])
                old_Count = int(data[0][2])

                info.execute(
                    f'UPDATE lecture SET Score={old_Score + mScore}, Count={old_Count + 1} WHERE Id={TargetId};')

            if TScore > 1:
                TScore -= 1

        info.connection.commit()

        await getChannel('_Report').send(
            f'[Command]Group lect - ans_check used by member {ctx.author.id}. {now_time_info("whole")}')

    @lect.command()
    async def end(self, ctx, day: int):

        if not role_check(ctx.author.roles, ['總召', 'Administrator']):
            await ctx.send(':no_entry_sign: You can\'t use that command!')
            return

        info.execute(f'SELECT Status FROM lecture_list WHERE Week={day};')
        data = info.fetchall()[0]

        if data[0] == 0:
            await ctx.send(':exclamation: The lecture has already ended!')
            return

        await ctx.send(':loudspeaker: @here, 講座結束了!\n :partying_face: 感謝大家今天的參與!')

        info.execute(f'UPDATE lecture_list SET Status=0 WHERE Week={day};')

        # adding scores and show lecture final data
        info.execute("SELECT * FROM lecture ORDER BY Score ASC")
        data = info.fetchall()
        if len(data) == 0:
            await ctx.send(':exclamation: There are no data to show!')
            return
        else:
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
                await getChannel('_ToMV').send(f'lect_crt {member[0]} {member[1]}')
                ranking += 1

            await ctx.send(embed=create_embed(':scroll: Lecture Event Result', 0x42fcff, ['Lecture final info'], [data_members]))

        info.execute('DELETE FROM lecture')
        info.connection.commit()

        await getChannel('_Report').send(
            f'[Command]Group lect - end used by member {ctx.author.id}. {now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Lecture(bot))
