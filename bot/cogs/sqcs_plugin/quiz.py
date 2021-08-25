from discord.ext import commands, tasks
from ...core.db.jsonstorage import JsonApi
from ...core.db.mongodb import Mongo
from ...core.utils import Time, DiscordExt
from ...core.fluctlight_ext import guild_weekly_update, Fluct
from ...core.cog_config import CogExtension
import discord


class Quiz(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator', '學術')
    async def quiz(self, ctx):
        pass

    # push back stand by answer
    @quiz.command()
    async def alter_standby_ans(self, ctx, alter_answer: str):
        """cmd
        修改下次的懸賞答案。

        .alter_answer: 下次的懸賞答案
        """
        quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')

        execute = {
            "$set": {
                "stand_by_answer": alter_answer
            }
        }
        quiz_set_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: 預備答案被設定為 {alter_answer} 了！')

    @quiz.command()
    async def alter_formal_ans(self, ctx, alter_answer: str):
        """cmd
        修改本次的懸賞答案。

        .alter_answer: 新的本次的懸賞答案
        """
        quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')

        execute = {
            "$set": {
                "correct_answer": alter_answer
            }
        }
        quiz_set_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: 正式答案被設定為 {alter_answer} 了！')

    @quiz.command()
    async def set_qns_link(self, ctx, qns_link: str):
        """cmd
        設定問題連結。

        .qns_link: 問題連結
        """
        quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')

        execute = {
            "$set": {
                "qns_link": qns_link
            }
        }
        quiz_set_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: 問題連結被設定為 {qns_link} 了！')

    @quiz.command()
    async def set_ans_link(self, ctx, ans_link: str):
        """cmd
        設定答案連結。

        .qns_link: 答案連結
        """
        quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')

        execute = {
            "$set": {
                "ans_link": ans_link
            }
        }
        quiz_set_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: 答案連結被設定為 {ans_link} 了！')

    @quiz.command()
    async def alt_member_result(self, ctx, member_id: int, new_result: int):
        if new_result not in [0, 1]:
            return await ctx.send(':x: 答題正確狀態參數必須為 0 或 1！')

        quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')
        execute = {
            "$set": {
                "correct": bool(new_result)
            }
        }
        quiz_set_cursor.update_one({"_id": member_id}, execute)

        member_name = await DiscordExt.get_member_nick_name(ctx.guild, member_id)
        await ctx.send(f'成員 {member_name} 的答題正確狀態被設定為 {new_result} 了！')

    @quiz.command()
    async def repost_qns(self, ctx):
        """cmd
        重新公告問題。
        """
        await ctx.message.delete()
        quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')
        qns_link = quiz_set_cursor.find_one({"_id": 0})["qns_link"]
        await ctx.send(
            f':exclamation: 以下為更新後的問題！\n'
            f'{qns_link}'
        )

    @quiz.command()
    async def repost_ans(self, ctx):
        """cmd
        重新公告答案。
        """
        await ctx.message.delete()
        quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')
        ans_link = quiz_set_cursor.find_one({"_id": 0})["ans_link"]
        await ctx.send(
            f':exclamation: 以下為更新後的解答！\n'
            f'{ans_link}'
        )

    # event answer listen function
    @commands.Cog.listener()
    async def on_message(self, msg):
        quiz_channel = self.bot.get_channel(746014424086610012)
        if quiz_channel is None:
            return

        if msg.author == self.bot.user or msg.channel != quiz_channel:
            return

        if msg.content.startswith('~') or msg.content.startswith('+'):
            return

        quiz_set_cursor, quiz_cursor = Mongo('sqcs-bot').get_curs(['QuizSetting', 'QuizOngoing'])

        quiz_status = quiz_set_cursor.find_one({"_id": 0})["event_status"]
        if not quiz_status:
            return

        await msg.delete()

        # whether the member had submit answer
        data = quiz_cursor.find_one({"_id": msg.author.id})
        if data:
            message = await JsonApi.get_humanity('quiz/repeat_answer')
            try:
                return await msg.author.send(message)
            except BaseException:
                pass

        # if answer fit standard format
        if msg.content.startswith('||') and msg.content.endswith('||'):
            correct_answer = quiz_set_cursor.find_one({"_id": 0})["correct_answer"]

            fluct_ext = Fluct(member_id=msg.author.id, score_mode='quiz')

            answer_correctness = (msg.content[2:-2].lower() == correct_answer)
            member_quiz_result = {
                "_id": msg.author.id,
                "correct": answer_correctness
            }
            quiz_cursor.insert_one(member_quiz_result)
            await fluct_ext.active_log_update()
            await fluct_ext.quiz_submit_update()

            message = await JsonApi.get_humanity('quiz/get_answer')
            try:
                await msg.author.send(message)
            except BaseException:
                pass

            # add score to member fluctlight if answer is correct
            if answer_correctness:
                await fluct_ext.add_score()
                await fluct_ext.quiz_correct_update()
        else:
            message = await JsonApi.get_humanity('quiz/invalid_syntax/pt_1', '\n')
            message += await JsonApi.get_humanity('quiz/answer_tut', '\n')
            message += await JsonApi.get_humanity('quiz/invalid_syntax/pt_2')
            try:
                await msg.author.send(message)
            except BaseException:
                pass


class QuizAuto(CogExtension):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')

        self.quiz_auto.start()

    @tasks.loop(minutes=5)
    async def quiz_auto(self):
        await self.bot.wait_until_ready()

        report_guild = self.bot.get_guild(784607509629239316)
        report_channel = discord.utils.get(report_guild.text_channels, name='sqcs-report')

        quiz_status = self.quiz_set_cursor.find_one({"_id": 0})["event_status"]

        def quiz_ready_to_start():
            return Time.get_info('week_day') == 1 and Time.get_info('hour') >= 6 and not quiz_status

        def quiz_ready_to_end():
            return Time.get_info('week_day') == 7 and Time.get_info('hour') >= 22 and quiz_status

        if quiz_ready_to_start():
            await quiz_start(self.bot)
            await report_channel.send(f'[AUTO QUIZ START][{Time.get_info("whole")}]')
        elif quiz_ready_to_end():
            await quiz_end(self.bot)
            await report_channel.send(f'[AUTO QUIZ END][{Time.get_info("whole")}]')


# auto start quiz event
async def quiz_start(bot):
    guild = bot.get_guild(743507979369709639)
    main_channel = bot.get_channel(746014424086610012)
    gm_channel = bot.get_channel(743677861000380527)

    quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')
    quiz_data = quiz_set_cursor.find_one({"_id": 0})
    stand_by_answer = quiz_data["stand_by_answer"]

    new_quiz_info = {
        "$set": {
            "event_status": True,
            "correct_answer": stand_by_answer,
            "stand_by_answer": 'N/A'
        }
    }
    quiz_set_cursor.update_one({"_id": 0}, new_quiz_info)

    # data re-check
    new_quiz_data = quiz_set_cursor.find_one({"_id": 0})
    quiz_status = new_quiz_data["event_status"]
    correct_answer = new_quiz_data["correct_answer"]

    await gm_channel.send(
        f'Quiz Event status set to {quiz_status}, '
        f'correct answer set to {correct_answer}!'
    )

    msg = await JsonApi.get_humanity('quiz/start/pt_1', '\n')
    msg += await JsonApi.get_humanity('quiz/answer_tut', '\n')
    msg += await JsonApi.get_humanity('quiz/start/pt_2')
    await main_channel.send(msg)
    await main_channel.send(f'活動開始於 {Time.get_info("whole")}')

    question_link = quiz_data["qns_link"]
    if question_link != '':
        await main_channel.send(
            f'以下為題目：\n'
            f'{question_link}'
        )

    await main_channel.set_permissions(guild.default_role, send_messages=True)


# auto end quiz event
async def quiz_end(bot):
    guild = bot.get_guild(743507979369709639)
    main_channel = bot.get_channel(746014424086610012)
    gm_channel = bot.get_channel(743677861000380527)

    quiz_set_cursor = Mongo('sqcs-bot').get_cur('QuizSetting')
    quiz_data = quiz_set_cursor.find_one({"_id": 0})
    old_correct_ans = quiz_data["correct_answer"]
    answer_link = quiz_data["ans_link"]

    execute = {
        "$set": {
            "correct_answer": 'N/A',
            "event_status": False,
            "qns_link": '',
            "ans_link": ''
        }
    }
    quiz_set_cursor.update_one({"_id": 0}, execute)

    # data re-check
    new_quiz_data = quiz_set_cursor.find_one({"_id": 0})
    quiz_status = new_quiz_data["event_status"]
    correct_answer = new_quiz_data["correct_answer"]

    await gm_channel.send(
        f'Quiz Event status set to {quiz_status}, '
        f'correct answer set to {correct_answer}!'
    )

    quiz_ongoing_cursor = Mongo('sqcs-bot').get_cur('QuizOngoing')
    fluctlight_cursor = Mongo('LightCube').get_cur('MainFluctlights')
    msg = await JsonApi.get_humanity('quiz/end/main/pt_1', '\n')
    msg += f':white_check_mark: 這次的答案呢...是 `{old_correct_ans}`！\n'
    msg += await JsonApi.get_humanity('quiz/end/main/pt_2', '\n')

    attend_count = quiz_ongoing_cursor.find({}).count()
    countable_member_count = fluctlight_cursor.find({"deep_freeze": {"$eq": False}}).count()
    quiz_attend_level = int(attend_count / countable_member_count)

    quiz_attend_level = min(quiz_attend_level, 7)

    msg += f'我這次有 {round((attend_count / countable_member_count) * 100, 1)} 分飽！\n'
    msg += await JsonApi.get_humanity(f'quiz/end/reactions/{quiz_attend_level}')
    await main_channel.send(msg)
    await main_channel.send(f':stopwatch: 活動結束於 {Time.get_info("whole")}')

    if answer_link != '':
        await main_channel.send(
            f'以下為解答：\n'
            f'{answer_link}'
        )

    await main_channel.set_permissions(guild.default_role, send_messages=False)

    # list the winners
    data = quiz_ongoing_cursor.find({"correct": {"$eq": True}})

    winners = ''
    for winner in data:
        winner_name = await DiscordExt.get_member_nick_name(guild, winner["_id"])
        winners += f'{winner_name}\n'

    if not winners:
        winners = 'None'

    quiz_ongoing_cursor.delete_many({})

    embed_para = [
        ':scroll: Quiz Event Result',
        'default',
        0x42fcff,
        ['Winner'],
        [winners]
    ]
    await main_channel.send(embed=await DiscordExt.create_embed(*embed_para))
    await guild_weekly_update(bot)


def setup(bot):
    bot.add_cog(Quiz(bot))
    bot.add_cog(QuizAuto(bot))
