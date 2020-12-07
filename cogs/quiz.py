from discord.ext import commands
from functions import *
import discord
import json
from core.classes import Cog_Extension


class Quiz(Cog_Extension):

    @commands.group()
    async def quiz(self, ctx):
        pass

    # push back stand by answer
    @quiz.command()
    async def quiz_push(self, ctx, msg):
        if (role_check(ctx.author.roles, ['總召', 'Administrator']) == False):
            await ctx.send('You can\'t use this command!')
            return

        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()

        if (quiz_data['stand_by_ans'] != 'N/A'):
            await ctx.send(f'The stand-by answer had already been set as {quiz_data["stand_by_ans"]}!')
            return

        quiz_data['stand_by_ans'] = msg

        await ctx.send(f'The stand-by answer has been set as {quiz_data["stand_by_ans"]}!')

        temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
        json.dump(quiz_data, temp_file)
        temp_file.close()

        await getChannel(self.bot, '_Report').send(f'[Command]Group quiz - quiz_push used by member {ctx.author.id}. {now_time_info("whole")}')


    # event answer listen function
    @commands.Cog.listener()
    async def on_message(self, msg):
        main_channel = discord.utils.get(self.bot.guilds[0].text_channels, name='懸賞區')
        if (msg.author == self.bot.user or msg.channel != main_channel or msg.content[0] == '~'):
            return

        temp_file = open('jsons/quiz.json', mode='r', encoding='utf8')
        quiz_data = json.load(temp_file)
        temp_file.close()
        print(quiz_data)

        if (quiz_data["event_status"] == 'False'):
            return

        await msg.delete()

        answered = int(-1)
        try:
            answered = quiz_data['answered_member'].index(msg.author.id)
        except:
            pass

        if (answered != -1):
            await msg.author.send('你已經傳送過答案了，請不要重複傳送！')
            return

        # print(msg.content[0:2], msg.content[-2:], msg.content[2:-2])
        if (msg.content[0:2] == '||' and msg.content[-2:] == '||'):
            await msg.author.send('我收到你的答案了!')
            quiz_data["answered_member"].append(msg.author.id)

            if (msg.content[2:-2] == quiz_data["correct_ans"]):
                await getChannel(self.bot, '_ToMV').send(f'quiz_crt {msg.author.id}')
                await quiz_data['correct_ans_member'].append(msg.author.id)
        else:
            await msg.author.send('你的答案是錯誤的格式！')

        temp_file = open('jsons/quiz.json', mode='w', encoding='utf8')
        json.dump(quiz_data, temp_file)
        temp_file.close()



def setup(bot):
    bot.add_cog(Quiz(bot))