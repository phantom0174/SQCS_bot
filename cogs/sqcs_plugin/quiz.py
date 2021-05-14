from discord.ext import commands
import discord
from core.db import self_client, rsp, fluctlight_client
from core.utils import Time, DiscordExt
from core.fluctlight_ext import guild_weekly_update, Fluct
from core.cog_config import CogExtension


class Quiz(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz(self, ctx):
        pass

    # push back stand by answer
    @quiz.command()
    async def alter_standby_ans(self, ctx, alter_answer: str):
        quiz_set_cursor = self_client["QuizSetting"]

        execute = {
            "$set": {
                "stand_by_answer": alter_answer
            }
        }
        quiz_set_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: 預備答案被設定為 {alter_answer} 了！')

    @quiz.command()
    async def alter_formal_ans(self, ctx, alter_answer: str):
        quiz_set_cursor = self_client["QuizSetting"]

        execute = {
            "$set": {
                "correct_answer": alter_answer
            }
        }
        quiz_set_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: 正式答案被設定為 {alter_answer} 了！')

    @quiz.command()
    async def set_qns_link(self, ctx, qns_link: str):
        quiz_set_cursor = self_client["QuizSetting"]

        execute = {
            "$set": {
                "qns_link": qns_link
            }
        }
        quiz_set_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: 問題連結被設定為 {qns_link} 了！')

    @quiz.command()
    async def set_ans_link(self, ctx, ans_link: str):
        quiz_set_cursor = self_client["QuizSetting"]

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

        quiz_set_cursor = self_client["QuizSetting"]
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
        await ctx.message.delete()
        quiz_set_cursor = self_client["QuizSetting"]
        qns_link = quiz_set_cursor.find_one({"_id": 0})["qns_link"]
        await ctx.send(
            f':exclamation: 以下為更新後的問題！\n'
            f'{qns_link}'
        )

    @quiz.command()
    async def repost_ans(self, ctx):
        await ctx.message.delete()
        quiz_set_cursor = self_client["QuizSetting"]
        ans_link = quiz_set_cursor.find_one({"_id": 0})["ans_link"]
        await ctx.send(
            f':exclamation: 以下為更新後的解答！\n'
            f'{ans_link}'
        )

    # event answer listen function
    @commands.Cog.listener()
    async def on_message(self, msg):
        quiz_channel = msg.guild.get_channel(746014424086610012)
        if quiz_channel is None:
            return

        if msg.author == self.bot.user or msg.channel != quiz_channel:
            return

        if msg.content.startswith('~') or msg.content.startswith('+'):
            return

        quiz_set_cursor = self_client["QuizSetting"]
        score_set_cursor = self_client["ScoreSetting"]
        fl_cursor = fluctlight_client["MainFluctlights"]

        quiz_status = quiz_set_cursor.find_one({"_id": 0})["event_status"]
        if not quiz_status:
            return

        await msg.delete()

        correct_answer = quiz_set_cursor.find_one({"_id": 0})["correct_answer"]
        quiz_score = score_set_cursor.find_one({"_id": 0})["quiz_point"]
        score_weight = score_set_cursor.find_one({"_id": 0})["score_weight"]
        quiz_cursor = self_client["QuizOngoing"]

        data = quiz_cursor.find_one({"_id": msg.author.id})
        if data:
            message = ':no_entry_sign: ' + '\n'.join(rsp["quiz"]["repeat_answer"])
            return await msg.author.send(message)

        if msg.content.startswith('||') and msg.content.endswith('||'):
            message = ':white_check_mark: ' + '\n'.join(rsp["quiz"]["get_answer"])
            await msg.author.send(message)

            answer_correctness = (msg.content[2:-2] == correct_answer)
            member_quiz_result = {
                "_id": msg.author.id,
                "correct": answer_correctness
            }
            quiz_cursor.insert_one(member_quiz_result)
            Fluct().active_log_update(msg.author.id)
            Fluct().quiz_submit_update(msg.author.id)

            # add score to member fluctlight
            if answer_correctness:
                execute = {
                    "$inc": {
                        "score": round(quiz_score * score_weight, 2)
                    }
                }
                fl_cursor.update_one({"_id": msg.author.id}, execute)
                Fluct().quiz_correct_update(msg.author.id)

        else:
            message = ':exclamation: ' + '\n'.join(rsp["quiz"]["invalid_syntax"]["pt_1"]) + '\n'
            message += '\n'.join(rsp["quiz"]["answer_tut"]) + '\n'
            message += '\n'.join(rsp["quiz"]["invalid_syntax"]["pt_2"])
            await msg.author.send(message)


# auto start quiz event
async def quiz_start(bot):
    guild = bot.guilds[0]
    main_channel = bot.get_channel(746014424086610012)
    gm_channel = bot.get_channel(743677861000380527)

    quiz_set_cursor = self_client["QuizSetting"]
    quiz_data = quiz_set_cursor.find_one({"_id": 0})
    stand_by_answer = quiz_data["stand_by_answer"]

    new_quiz_info = {
        "$set": {
            "event_status": True,
            "correct_answer": stand_by_answer,
            "stand_by_answer": 'N/A'
        }
    }
    quiz_set_cursor.update({"_id": 0}, new_quiz_info)

    # data re-check
    new_quiz_data = quiz_set_cursor.find_one({"_id": 0})
    quiz_status = new_quiz_data["event_status"]
    correct_answer = new_quiz_data["correct_answer"]

    await gm_channel.send(
        f'Quiz Event status set to {quiz_status}, '
        f'correct answer set to {correct_answer}!'
    )

    msg = '\n'.join(rsp["quiz"]["start"]["pt_1"]) + '\n'
    msg += '\n'.join(rsp["quiz"]["answer_tut"]) + '\n'
    msg += '\n'.join(rsp["quiz"]["start"]["pt_2"])
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
    guild = bot.guilds[0]
    main_channel = bot.get_channel(746014424086610012)
    gm_channel = bot.get_channel(743677861000380527)

    quiz_set_cursor = self_client["QuizSetting"]
    quiz_data = quiz_set_cursor.find_one({"_id": 0})
    old_correct_ans = quiz_data["correct_answer"]
    answer_link = quiz_data["ans_link"]

    execute = {
        "$set": {
            "correct_answer": 'N/A',
            "event_status": 0,
            "qns_link": '',
            "ans_link": ''
        }
    }
    quiz_set_cursor.update_one({"_id": 0}, execute)

    # data re-check
    new_quiz_dara = quiz_set_cursor.find_one({"_id": 0})
    quiz_status = new_quiz_dara["event_status"]
    correct_answer = new_quiz_dara["correct_answer"]

    await gm_channel.send(
        f'Quiz Event status set to {quiz_status}, '
        f'correct answer set to {correct_answer}!'
    )

    quiz_ongoing_cursor = self_client["QuizOngoing"]
    fluctlight_cursor = fluctlight_client["light-cube-info"]
    msg = '\n'.join(rsp["quiz"]["end"]["main"]["pt_1"]) + '\n'
    msg += f':white_check_mark: 這次的答案呢...是 `{old_correct_ans}`！\n'
    msg += '\n'.join(rsp["quiz"]["end"]["main"]["pt_2"]) + '\n'

    attend_count = quiz_ongoing_cursor.find({}).count()
    countable_member_count = fluctlight_cursor.find({"deep_freeze": {"$eq": 0}}).count()
    quiz_attend_level = int(attend_count / countable_member_count)

    quiz_attend_level = min(quiz_attend_level, 7)

    msg += f'我這次有 {round((attend_count / countable_member_count) * 100, 1)} 分飽！\n'
    msg += rsp["quiz"]["end"]["reactions"][quiz_attend_level]
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

    winners = str()
    for winner in data:
        winner_name = await DiscordExt.get_member_nick_name(bot.gulids[0], winner["_id"])
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
    await main_channel.send(embed=DiscordExt.create_embed(*embed_para))
    await guild_weekly_update(bot)


def setup(bot):
    bot.add_cog(Quiz(bot))
