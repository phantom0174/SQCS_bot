from discord.ext import commands
from functions import *
import discord
import asyncio
import random
from core.classes import Cog_Extension
from cogs.setup import *


class Lecture(Cog_Extension):

    @commands.group()
    async def lect(self, ctx):
        pass

    @lect.command()
    async def start(self, ctx, *, msg):
        if (role_check(ctx.author.roles, ['總召', 'Administrator']) == False):
            await ctx.send('You can\'t use that command!')
            return

        temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
        lecture_data = json.load(temp_file)
        temp_file.close()

        if (lecture_data['event_status'] == 'True'):
            await ctx.send('The lecture has already started!')
            return

        day = msg.split(' ')[0]

        await ctx.send('@everyone，講座開始了！\n 於回答講師問題時請在答案前方加上"&"，回答正確即可加分。')

        lecture_data['event_status'] = 'True'

        def check(message):
            return message.channel == getChannel(self.bot, '_ToMV')

        await getChannel(self.bot, '_ToMV').send('request_score_weight')
        sw = int((await self.bot.wait_for('message', check=check, timeout=30.0)).content)

        lecture_data['temp_sw'] = sw

        temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
        json.dump(lecture_data, temp_file)
        temp_file.close()

        msg_logs = await ctx.channel.history(limit=200).flatten()
        for msg in msg_logs:
            if (len(msg.content) > 0 and msg.content[0] == '&'):
                await msg.delete()

        # cd time from preventing member leave at once
        random.seed(now_time_info('hour') * 92384)
        await asyncio.sleep(random.randint(30, 180))

        # add score to the attendances

        if (day == '5'):
            voice_channel = discord.utils.get(ctx.guild.voice_channels, name='星期五晚上固定講座')
        elif (day == '7'):
            voice_channel = discord.utils.get(ctx.guild.voice_channels, name='量子電腦硬體')

        for member in voice_channel.members:
            await getChannel(self.bot, '_ToMV').send(f'lecture_attend {member.id}')

        await getChannel(self.bot, '_Report').send(f'[Command]Group lect - start used by member {ctx.author.id}. {now_time_info("whole")}')

    # lecture ans check
    @lect.command()
    async def ans_check(self, ctx, *, msg):
        CrtAns = msg.split(' ')
        msg_logs = await ctx.channel.history(limit=100).flatten()
        MemberCrtMsg = []  # correct message

        for msg in msg_logs:
            if (len(msg.content) == 0):
                continue

            if (msg.author.bot == False and msg.content[0] == '&'):
                await msg.delete()
                for ans in CrtAns:
                    # correct answer is a subset of member answer
                    if (msg.content.find(ans) != -1):
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

            if (len(data) == 0):
                info.execute(f'INSERT INTO lecture VALUES({TargetId}, {mScore}, 1);')
            else:
                old_Score = float(data[0][1])
                old_Count = int(data[0][2])

                info.execute(
                    f'UPDATE lecture SET Score={old_Score + mScore}, Count={old_Count + 1} WHERE Id={TargetId};')

            if (TScore > 1):
                TScore -= 1

        info.connection.commit()

        await getChannel(self.bot, '_Report').send(f'[Command]Group lect - ans_check used by member {ctx.author.id}. {now_time_info("whole")}')

    @lect.command()
    async def end(self, ctx):

        if (role_check(ctx.author.roles, ['總召', 'Administrator']) == False):
            await ctx.send('You can\'t use that command!')
            return

        temp_file = open('jsons/lecture.json', mode='r', encoding='utf8')
        lecture_data = json.load(temp_file)
        temp_file.close()

        if (lecture_data['event_status'] == 'False'):
            await ctx.send('The lecture has already ended!')
            return

        await ctx.send('@here, the lecture has ended!')

        lecture_data['event_status'] = 'False'

        temp_file = open('jsons/lecture.json', mode='w', encoding='utf8')
        json.dump(lecture_data, temp_file)
        temp_file.close()

        # adding scores and show lecture final data
        info.execute("SELECT * FROM lecture ORDER BY Score DESC")
        data = info.fetchall()
        if (len(data) == 0):
            await ctx.send('There are no data to show!')
            return
        else:
            data_members = str()
            for member in data:
                member_obj = await self.bot.fetch_user(member[0])  # member id
                data_members += f'{member_obj.name}:: Score: {member[1]}, Answer Count: {member[2]}\n'
                await getChannel(self.bot, '_ToMV').send(f'lect_crt {member[0]} {member[1]}')

            await ctx.send(embed=create_embed('Lecture Event Result', 0x42fcff, ['Lecture final info'], [data_members]))

        info.execute('DELETE FROM lecture')
        info.connection.commit()

        await getChannel(self.bot, '_Report').send(f'[Command]Group lect - end used by member {ctx.author.id}. {now_time_info("whole")}')



def setup(bot):
    bot.add_cog(Lecture(bot))