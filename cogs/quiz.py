from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client, link
import functions as func
import discord
import json
from pymongo import MongoClient


class Quiz(Cog_Extension):

    @commands.group()
    async def quiz(self, ctx):
        pass

    # push back stand by answer
    @quiz.command()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz_push(self, ctx, msg):

        with open('jsons/quiz.json', mode='r', encoding='utf8') as temp_file:
            quiz_data = json.load(temp_file)

        if quiz_data['stand_by_ans'] != 'N/A':
            await ctx.send(f':exclamation: The stand-by answer had already been set as {quiz_data["stand_by_ans"]}!')
            return

        quiz_data['stand_by_ans'] = msg

        await ctx.send(f':white_check_mark: The stand-by answer has been set as {quiz_data["stand_by_ans"]}!')

        with open('jsons/quiz.json', mode='w', encoding='utf8') as temp_file:
            json.dump(quiz_data, temp_file)

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group quiz - quiz_push used by member {ctx.author.id}. {func.now_time_info("whole")}')

    # event answer listen function
    @commands.Cog.listener()
    async def on_message(self, msg):
        main_channel = discord.utils.get(self.bot.guilds[0].text_channels, name='懸賞區')
        if msg.author == self.bot.user or msg.channel != main_channel or msg.content[0] == '~':
            return

        with open('jsons/quiz.json', mode='r', encoding='utf8') as temp_file:
            quiz_data = json.load(temp_file)

        if quiz_data["event_status"] == 'False':
            return

        await msg.delete()

        quiz_cursor = client["quiz_event"]
        data = quiz_cursor.find({})

        if data is not None:
            await msg.author.send(':no_entry_sign: 你已經傳送過答案了，請不要重複傳送！')
            return

        if msg.content[0:2] == '||' and msg.content[-2:] == '||':
            await msg.author.send(':white_check_mark: 我收到你的答案了!')
            member_quiz_info = {"_id": msg.author.id, "correct": 0}
            quiz_cursor.insert_one(member_quiz_info)

            if msg.content[2:-2] == quiz_data["correct_ans"]:

                fl_client = MongoClient(link)["LightCube"]
                fl_cursor = fl_client["light-cube-info"]
                fl_cursor.update_one({"_id": msg.author.id}, {"$set": {"correct": 1}})

                if fl_cursor.find_one({"_id": msg.author.id})["week_active"] is 0:
                    fl_cursor.update_one({"_id": msg.author.id}, {"$set": {"week_active": 1}})

        else:
            await msg.author.send(':exclamation: 你的答案是錯誤的格式！')


# auto start quiz event
async def quiz_start(bot):
    guild = bot.guilds[0]
    main_channel = discord.utils.get(guild.text_channels, name='懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='◉總指令區')

    with open('jsons/quiz.json', mode='r', encoding='utf8') as temp_file:
        quiz_data = json.load(temp_file)

    quiz_data['event_status'] = "True"
    quiz_data['correct_ans'] = quiz_data['stand_by_ans']
    quiz_data['stand_by_ans'] = 'N/A'

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')

    await main_channel.send(':loudspeaker: @everyone，有一個新的懸賞活動開始了，請確認你的答案是隱蔽模式！\n :exclamation: (請在答案的前方與後方各加上"||"的符號)')
    await main_channel.send(f'活動開始於 {func.now_time_info("whole")}')
    await main_channel.set_permissions(guild.default_role, send_messages=True)

    with open('jsons/quiz.json', mode='w', encoding='utf8') as temp_file:
        json.dump(quiz_data, temp_file)


# auto end quiz event
async def quiz_end(bot):
    guild = bot.guilds[0]
    main_channel = discord.utils.get(guild.text_channels, name='懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='◉總指令區')

    with open('jsons/quiz.json', mode='r', encoding='utf8') as temp_file:
        quiz_data = json.load(temp_file)

    quiz_data['event_status'] = "False"

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_data["event_status"]}, correct answer set to {quiz_data["correct_ans"]}!')
    await main_channel.set_permissions(guild.default_role, send_messages=False)
    await main_channel.send(f':loudspeaker: @everyone，懸賞活動結束了！這周的正確答案是 {quiz_data["correct_ans"]}。\n :stopwatch: 活動結束於 {func.now_time_info("whole")}')

    quiz_data['correct_ans'] = "N/A"

    with open('jsons/quiz.json', mode='w', encoding='utf8') as temp_file:
        json.dump(quiz_data, temp_file)

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

    await main_channel.send(embed=func.create_embed(':scroll: Quiz Event Result', 0x42fcff, ['Winner'], [winners]))

    await func.getChannel(bot, '_ToMV').send('update_guild_fluctlight')


def setup(bot):
    bot.add_cog(Quiz(bot))
