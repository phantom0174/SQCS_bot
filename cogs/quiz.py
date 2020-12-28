from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client, link
import core.functions as func
import discord
import json
from pymongo import MongoClient
import core.score_module as sm


class Quiz(Cog_Extension):

    @commands.group()
    async def quiz(self, ctx):
        pass

    # push back stand by answer
    @quiz.command()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz_push(self, ctx, insert_answer: str):
        quiz_data_cursor = client["quiz_data"]

        stand_by_answer = quiz_data_cursor.find_one({"_id": 0})["stand_by_answer"]

        if stand_by_answer != 'N/A':
            await ctx.send(f':exclamation: The stand-by answer had already been set as {stand_by_answer}!')
            return

        quiz_data_cursor.update_one({"_id": 0}, {"$set": {"stand_by_answer": insert_answer}})
        await ctx.send(f':white_check_mark: The stand-by answer has been set as {insert_answer}!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group quiz - quiz_push used by member {ctx.author.id}. {func.now_time_info("whole")}')

    # event answer listen function
    @commands.Cog.listener()
    async def on_message(self, msg):
        main_channel = discord.utils.get(self.bot.guilds[0].text_channels, name='💎懸賞區')
        if msg.author == self.bot.user or msg.channel != main_channel or msg.content[0] == '~':
            return

        quiz_data_cursor = client["quiz_data"]
        quiz_status = quiz_data_cursor.find_one({"_id": 0})["event_status"]

        if quiz_status == 0:
            return

        await msg.delete()

        correct_answer = quiz_data_cursor.find_one({"_id": 0})["correct_answer"]

        mvisualizer_client = MongoClient(link)["mvisualizer"]
        quiz_score_cursor = mvisualizer_client["score_parameters"]
        quiz_score = quiz_score_cursor.find_one({"_id": 0})["quiz_point"]
        score_weight = quiz_score_cursor.find_one({"_id": 0})["score_weight"]

        quiz_cursor = client["quiz_event"]
        data = quiz_cursor.find_one({"_id": msg.author.id})

        if data is not None:
            await msg.author.send(':no_entry_sign: 你已經傳送過答案了，請不要重複傳送！')
            return

        if msg.content[0:2] == '||' and msg.content[-2:] == '||':
            await msg.author.send(':white_check_mark: 我收到你的答案了!')
            member_quiz_info = {"_id": msg.author.id, "correct": 0}
            quiz_cursor.insert_one(member_quiz_info)

            if msg.content[2:-2] == correct_answer:
                quiz_cursor.update_one({"_id": msg.author.id}, {"$set": {"correct": 1}})

                # add score to member fluctlight
                fl_client = MongoClient(link)["LightCube"]
                fl_cursor = fl_client["light-cube-info"]

                fl_cursor.update_one({"_id": msg.author.id}, {"$inc": {"score": quiz_score * score_weight}})

                await sm.active_log_update(msg.author.id)

        else:
            await msg.author.send(':exclamation: 你的答案是錯誤的格式！')


# auto start quiz event
async def quiz_start(bot):
    guild = bot.guilds[0]
    main_channel = discord.utils.get(guild.text_channels, name='💎懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='總指令區')

    quiz_event_cursor = client["quiz_data"]

    stand_by_answer = quiz_event_cursor.find_one({"_id": 0}, {"stand_by_answer": 1})["stand_by_answer"]
    new_quiz_info = {"event_status": 1, "correct_answer": stand_by_answer, "stand_by_answer": 'N/A'}
    quiz_event_cursor.update({"_id": 0}, new_quiz_info)

    # data re-check
    quiz_status = quiz_event_cursor.find_one({"_id": 0}, {"event_status": 1})["event_status"]
    correct_answer = quiz_event_cursor.find_one({"_id": 0}, {"correct_answer": 1})["correct_answer"]

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_status}, correct answer set to {correct_answer}!')

    await main_channel.send('@everyone\n'
                            ':loudspeaker: 新的懸賞活動開始了，請確認你的答案是隱蔽模式！\n'
                            ':exclamation: 請在答案的前方與後方各加上`||`符號\n'
                            f'活動開始於 {func.now_time_info("whole")}')

    await main_channel.set_permissions(guild.default_role, send_messages=True)


# auto end quiz event
async def quiz_end(bot):
    guild = bot.guilds[0]
    main_channel = discord.utils.get(guild.text_channels, name='💎懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='總指令')

    quiz_event_cursor = client["quiz_data"]
    quiz_event_cursor.update_one({"_id": 0}, {"event_status": 0})

    old_correct_ans = quiz_event_cursor.find_one({"_id": 0}, {"correct_answer": 1})["correct_answer"]
    quiz_event_cursor.update_one({"_id": 0}, {"correct_answer": 'N/A'})

    # data re-check
    quiz_status = quiz_event_cursor.find_one({"_id": 0}, {"event_status": 1})["event_status"]
    correct_answer = quiz_event_cursor.find_one({"_id": 0}, {"correct_answer": 1})["correct_answer"]

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_status}, correct answer set to {correct_answer}!')

    await main_channel.send(f'@everyone\n'
                            f':loudspeaker: 懸賞活動結束了！\n'
                            f':white_check_mark: 這周的正確答案是 `{old_correct_ans}`\n'
                            f':stopwatch: 活動結束於 {func.now_time_info("whole")}')

    await main_channel.set_permissions(guild.default_role, send_messages=False)

    # list the winners
    quiz_cursor = client["quiz_event"]
    data = quiz_cursor.find({"correct": {"$eq": 1}})

    winners = str()
    for winner in data:
        winner_name = (await bot.guilds[0].fetch_member(winner["_id"])).nick
        if winner_name is None:
            winner_name = (await bot.fetch_user(winner["_id"])).name
        winners += f'{winner_name}\n'

    if winners == '':
        winners = 'None'

    quiz_cursor.delete_many({})

    await main_channel.send(embed=func.create_embed(':scroll: Quiz Event Result', 0x42fcff, ['Winner'], [winners]))
    await func.getChannel(bot, '_ToMV').send('update_guild_fluctlight')


def setup(bot):
    bot.add_cog(Quiz(bot))
