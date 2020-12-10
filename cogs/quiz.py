from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import *
from functions import *
import discord
import json


class Quiz(Cog_Extension):

    @commands.group()
    async def quiz(self, ctx):
        pass

    # push back stand by answer
    @quiz.command()
    async def quiz_push(self, ctx, msg):
        if not role_check(ctx.author.roles, ['總召', 'Administrator']):
            await ctx.send(':no_entry_sign: You can\'t use this command!')
            return

        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if quiz_data['stand_by_ans'] != 'N/A':
            await ctx.send(f':exclamation: The stand-by answer had already been set as {quiz_data["stand_by_ans"]}!')
            return

        quiz_data['stand_by_ans'] = msg

        await ctx.send(f':white_check_mark: The stand-by answer has been set as {quiz_data["stand_by_ans"]}!')

        temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
        json.dump(quiz_data, temp_file)
        temp_file.close()

        await getChannel('_Report').send(
            f'[Command]Group quiz - quiz_push used by member {ctx.author.id}. {now_time_info("whole")}')

    # event answer listen function
    @commands.Cog.listener()
    async def on_message(self, msg):
        main_channel = discord.utils.get(self.bot.guilds[0].text_channels, name='懸賞區')
        if msg.author == self.bot.user or msg.channel != main_channel or msg.content[0] == '~':
            return

        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if quiz_data["event_status"] == 'False':
            return

        await msg.delete()

        info.execute(f'SELECT * FROM quiz WHERE Id={msg.author.id};')
        data = info.fetchall()

        if len(data) != 0:
            await msg.author.send(':no_entry_sign: 你已經傳送過答案了，請不要重複傳送！')
            return

        if msg.content[0:2] == '||' and msg.content[-2:] == '||':
            await msg.author.send(':white_check_mark: 我收到你的答案了!')
            info.execute(f'INSERT INTO quiz VALUES({msg.author.id}, 0);')

            if msg.content[2:-2] == quiz_data["correct_ans"]:
                await getChannel('_ToMV').send(f'quiz_crt {msg.author.id}')
                info.execute(f'UPDATE quiz SET Crt=1 WHERE Id={msg.author.id};')

        else:
            await msg.author.send(':exclamation: 你的答案是錯誤的格式！')

        info.connection.commit()


# auto start quiz event
async def quiz_start(bot):
    guild = bot.guilds[0]
    main_channel = discord.utils.get(guild.text_channels, name='懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='◉總指令區')

    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()

    quiz_data['event_status'] = "True"
    quiz_data['correct_ans'] = quiz_data['stand_by_ans']
    quiz_data['stand_by_ans'] = 'N/A'

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')

    await main_channel.send(':loud_speaker: @everyone，有一個新的懸賞活動開始了，請確認你的答案是隱蔽模式！\n :exclamation: (請在答案的前方與後方各加上"||"的符號)')
    await main_channel.send(f'活動開始於 {now_time_info("whole")}')
    await main_channel.set_permissions(guild.default_role, send_messages=True)

    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()


# auto end quiz event
async def quiz_end(bot):
    guild = bot.guilds[0]
    main_channel = discord.utils.get(guild.text_channels, name='懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='◉總指令區')

    temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
    quiz_data = json.load(temp_file)
    temp_file.close()

    quiz_data['event_status'] = "False"
    quiz_data['correct_ans'] = "N/A"

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
    await main_channel.set_permissions(guild.default_role, send_messages=False)
    await main_channel.send(f':stopwatch: 活動結束於 {now_time_info("whole")}')

    temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
    json.dump(quiz_data, temp_file)
    temp_file.close()

    # list the winners
    info.execute('SELECT * FROM quiz WHERE Crt=1;')
    data = info.fetchall()

    winners = str()
    for winner in data:
        member = await bot.fetch_user(winner[0])
        winners += f'{member.name}\n'

    if winners == '':
        winners += 'None'

    info.execute('DELETE FROM quiz;')
    info.connection.commit()

    await main_channel.send(embed=create_embed(':scroll: Quiz Event Result', 0x42fcff, ['Winner'], [winners]))

    await getChannel('_ToMV').send('update_guild_fluctlight')


def setup(bot):
    bot.add_cog(Quiz(bot))
