from discord.ext import commands
import discord
from core.setup import client, rsp, fluctlight_client
import core.functions as func
import core.score_module as sm
from core.vi_update import guild_weekly_update
from core.classes import CogExtension


class Quiz(CogExtension):

    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def quiz(self, ctx):
        pass

    # push back stand by answer
    @quiz.command()
    async def alter_standby_ans(self, ctx, alter_answer: str):
        quiz_data_cursor = client["quiz_data"]

        execute = {
            "$set": {
                "stand_by_answer": alter_answer
            }
        }
        quiz_data_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: The stand-by answer has been set as {alter_answer}!')

    @quiz.command()
    async def alter_formal_ans(self, ctx, alter_answer: str):
        quiz_data_cursor = client["quiz_data"]

        execute = {
            "$set": {
                "correct_answer": alter_answer
            }
        }
        quiz_data_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: The stand-by answer has been set as {alter_answer}!')

    @quiz.command()
    async def set_qns_link(self, ctx, qns_link: str):
        quiz_data_cursor = client["quiz_data"]

        execute = {
            "$set": {
                "qns_link": qns_link
            }
        }
        quiz_data_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: The question link has been set as {qns_link}!')

    @quiz.command()
    async def set_ans_link(self, ctx, ans_link: str):
        quiz_data_cursor = client["quiz_data"]

        execute = {
            "$set": {
                "ans_link": ans_link
            }
        }
        quiz_data_cursor.update_one({"_id": 0}, execute)
        await ctx.send(f':white_check_mark: The question link has been set as {ans_link}!')

    @quiz.command()
    async def alt_member_result(self, ctx, member_id: int, new_result: int):
        if new_result not in [0, 1]:
            await ctx.send(':exclamation: New result must be one of 0 or 1!')
            return

        quiz_cursor = client["quiz_data"]
        execute = {
            "$set": {
                "correct": new_result
            }
        }
        quiz_cursor.update_one({"_id": member_id}, execute)

        member_name = (await self.bot.fetch_user(member_id)).name
        await ctx.send(f"Member {member_name}'s correctness has been set as {new_result}!")

    @quiz.command()
    async def repost_qns(self, ctx):
        await ctx.message.delete()
        quiz_cursor = client["quiz_data"]
        qns_link = quiz_cursor.find_one({"_id": 0})["qns_link"]
        await ctx.send(
            f':exclamation: 以下為更新後的問題！\n'
            f'{qns_link}'
        )

    @quiz.command()
    async def repost_ans(self, ctx):
        await ctx.message.delete()
        quiz_cursor = client["quiz_data"]
        ans_link = quiz_cursor.find_one({"_id": 0})["ans_link"]
        await ctx.send(
            f':exclamation: 以下為更新後的解答！\n'
            f'{ans_link}'
        )

    # event answer listen function
    @commands.Cog.listener()
    async def on_message(self, msg):
        main_channel = discord.utils.get(self.bot.guilds[0].text_channels, name='💎懸賞區')
        if msg.author == self.bot.user or msg.channel != main_channel or msg.content[0] == '~' or msg.content[0] == '+':
            return

        quiz_data_cursor = client["quiz_data"]
        quiz_status = quiz_data_cursor.find_one({"_id": 0})["event_status"]

        if quiz_status == 0:
            return

        await msg.delete()

        correct_answer = quiz_data_cursor.find_one({"_id": 0})["correct_answer"]

        quiz_score_cursor = client["score_parameters"]
        quiz_score = quiz_score_cursor.find_one({"_id": 0})["quiz_point"]
        score_weight = quiz_score_cursor.find_one({"_id": 0})["score_weight"]

        quiz_cursor = client["quiz_event"]
        data = quiz_cursor.find_one({"_id": msg.author.id})

        if data:
            message = ':no_entry_sign: ' + '\n'.join(rsp["quiz"]["repeat_answer"])
            await msg.author.send(message)
            return

        if msg.content[:2] == '||' and msg.content[-2:] == '||':
            message = ':white_check_mark: ' + '\n'.join(rsp["quiz"]["get_answer"])
            await msg.author.send(message)

            answer_correctness = (msg.content[2:-2] == correct_answer)
            member_quiz_info = {
                "_id": msg.author.id,
                "correct": answer_correctness
            }
            quiz_cursor.insert_one(member_quiz_info)
            await sm.active_log_update(msg.author.id)

            # add score to member fluctlight
            if answer_correctness:
                fl_cursor = fluctlight_client["light-cube-info"]

                execute = {
                    "$inc": {
                        "score": quiz_score * score_weight
                    }
                }
                fl_cursor.update_one({"_id": msg.author.id}, execute)

        else:
            message = ':exclamation: ' + '\n'.join(rsp["quiz"]["invalid_syntax"]["pt_1"]) + '\n'
            message += '\n'.join(rsp["quiz"]["answer_tut"]) + '\n'
            message += '\n'.join(rsp["quiz"]["invalid_syntax"]["pt_2"])
            await msg.author.send(message)


# auto start quiz event
async def quiz_start(bot):
    guild = bot.guilds[0]
    main_channel = discord.utils.get(guild.text_channels, name='💎懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='總指令區')

    quiz_event_cursor = client["quiz_data"]

    quiz_data = quiz_event_cursor.find_one({"_id": 0})

    stand_by_answer = quiz_data["stand_by_answer"]

    new_quiz_info = {
        "$set": {
            "event_status": 1,
            "correct_answer": stand_by_answer,
            "stand_by_answer": 'N/A'
        }
    }
    quiz_event_cursor.update({"_id": 0}, new_quiz_info)

    # data re-check
    quiz_status = quiz_event_cursor.find_one({"_id": 0})["event_status"]
    correct_answer = quiz_event_cursor.find_one({"_id": 0})["correct_answer"]

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_status}, '
        f'correct answer set to {correct_answer}!'
    )

    msg = '\n'.join(rsp["quiz"]["start"]["pt_1"]) + '\n'
    msg += '\n'.join(rsp["quiz"]["answer_tut"]) + '\n'
    msg += '\n'.join(rsp["quiz"]["start"]["pt_2"])
    await main_channel.send(msg)
    await main_channel.send(f'活動開始於 {func.now_time_info("whole")}')

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
    main_channel = discord.utils.get(guild.text_channels, name='💎懸賞區')
    cmd_channel = discord.utils.get(guild.text_channels, name='總指令區')

    quiz_event_cursor = client["quiz_data"]

    quiz_data = quiz_event_cursor.find_one({"_id": 0})
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
    quiz_event_cursor.update_one({"_id": 0}, execute)

    # data re-check
    quiz_status = quiz_event_cursor.find_one({"_id": 0})["event_status"]
    correct_answer = quiz_event_cursor.find_one({"_id": 0})["correct_answer"]

    await cmd_channel.send(
        f'Quiz Event status set to {quiz_status}, '
        f'correct answer set to {correct_answer}!'
    )

    quiz_cursor = client["quiz_event"]
    fluctlight_cursor = fluctlight_client["light-cube-info"]
    msg = '\n'.join(rsp["quiz"]["end"]["main"]["pt_1"]) + '\n'
    msg += f':white_check_mark: 這次的答案呢...是 `{old_correct_ans}`！\n'
    msg += '\n'.join(rsp["quiz"]["end"]["main"]["pt_2"]) + '\n'

    attend_count = quiz_cursor.find({}).count()
    quiz_attend_per = fluctlight_cursor.find({"deep_freeze": {"$eq": 0}}).count()
    quiz_attend_level = int(attend_count / quiz_attend_per)

    quiz_attend_level = min(quiz_attend_level, 7)

    msg += f'我這次有 {round((attend_count / quiz_attend_per) * 100, 1)} 分飽！\n'
    msg += rsp["quiz"]["end"]["reactions"][quiz_attend_level]
    await main_channel.send(msg)
    await main_channel.send(f':stopwatch: 活動結束於 {func.now_time_info("whole")}')

    if answer_link != '':
        await main_channel.send(
            f'以下為解答：\n'
            f'{answer_link}'
        )

    await main_channel.set_permissions(guild.default_role, send_messages=False)

    # list the winners
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

    embed_para = [
        ':scroll: Quiz Event Result',
        'default',
        0x42fcff,
        ['Winner'],
        [winners]
    ]
    await main_channel.send(embed=func.create_embed(*embed_para))

    await guild_weekly_update(bot)


def setup(bot):
    bot.add_cog(Quiz(bot))
