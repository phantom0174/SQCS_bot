from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import client, rsp, fluctlight_client
import core.functions as func
import discord


class Kick_Member(Cog_Extension):

    @commands.group()
    async def kick(self, ctx):
        pass

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][kick][list]')

        await ctx.send(':hourglass_flowing_sand: Finding...')

        kick_member_cursor = client["kick_member_list"]
        data = kick_member_cursor.find({})

        if data.count() == 0:
            await ctx.send(':exclamation: There are no member in the kick list!')
            return

        kick_member_list = str()
        for member in data:
            kick_member_list += f'Id: {member["_id"]}, Name: {member["name"]}, Contrib: {member["contrib"]}, lvl_ind: {member["lvl_ind"]}\n'

            if len(kick_member_list) > 1600:
                await ctx.send(kick_member_list)
                kick_member_list = ''

        if len(kick_member_list) > 0:
            await ctx.send(kick_member_list)

        await ctx.send(':white_check_mark: Logging finished!')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def add(self, ctx, member_id: int):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][kick][add][member_id: {member_id}]')

        fluctlight_cursor = fluctlight_client["light-cube-info"]
        data = fluctlight_cursor.find_one({"_id": member_id}, {"contrib": 1, "lvl_ind": 1})

        if data.count() == 0:
            await ctx.send(f':exclamation: There\'re no data of member whose id is {member_id}')
            return

        member_contrib = data["contrib"]
        member_lvl_ind = data["lvl_ind"]

        member = await ctx.guild.fetch_member(member_id)
        member_name = member.nick
        if member_name is None:
            member_name = member.name

        member_info = {
            "_id": member_id,
            "name": member_name,
            "contrib": member_contrib,
            "lvl_ind": member_lvl_ind
        }

        kick_member_cursor = client["kick_member_list"]
        kick_member_cursor.insert_one(member_info)

        await ctx.send(f':white_check_mark: Member {member_name}({member_id}) has been added to the kick list!')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remove(self, ctx, member_id: int):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][kick][remove][member_id: {member_id}]')

        kick_member_cursor = client["kick_member_list"]
        data = kick_member_cursor.find_one({"_id": member_id})

        if data.count() == 0:
            await ctx.send(f':exclamation: Member {member_id} isn\'t in the kick list!')
            return

        kick_member_cursor.delete_one({"_id": member_id})

        await ctx.send(f':white_check_mark: Member {member_id} has been removed from the kick list!')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def kick_single(self, ctx, member_id: int, kick_reason: str):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][kick][kick_single][member_id: {member_id}, kick_reason: {kick_reason}]')

        kick_member_cursor = client["kick_member_list"]
        data = kick_member_cursor.find_one({"_id": member_id})

        if data.count() == 0:
            await ctx.send(f':exclamation: Member {member_id} isn\'t in the kick list!')
            return

        kick_user = await ctx.guild.fetch_member(member_id)

        if kick_reason == 'default':
            kick_reason = f':skull_crossbones: Levelling index reached {data["lvl_ind"]}.'

        msg = '\n'.join(rsp["kick"]["kick_single"]) + '\n'
        msg += f'> {kick_reason}\n'
        msg += '\n'.join(rsp["kick"]["re_join"])
        await kick_user.send(msg)

        try:
            await kick_user.kick(reason=kick_reason)
        except Exception as e:
            await ctx.send(f':x: Error when kicking member {data["name"]}({data["_id"]})!')
            await ctx.send(content=e, delete_after=5.0)

        fluctlight_cursor = fluctlight_client["light-cube-info"]
        active_logs_cursor = fluctlight_client["active_logs"]

        try:
            fluctlight_cursor.delete_one({"_id": member_id})
            active_logs_cursor.delete_one({"_id": member_id})
        except Exception as e:
            await ctx.send(f':x: Error when deleting member {data["name"]}({data["_id"]})\'s fluctlight data!')
            await ctx.send(content=e, delete_after=5.0)

        kick_member_cursor.delete_one({"_id": member_id})
        await ctx.send(f':white_check_mark: Kicked member {data["name"]}({data["_id"]})!')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def kick_all(self, ctx):
        await func.report_cmd(self.bot, ctx, f'[CMD EXECUTED][kick][kick_all]')

        kick_member_cursor = client["kick_member_list"]
        data = kick_member_cursor.find({})

        if data.count() == 0:
            await ctx.send(':exclamation: Kick member list is empty!')
            return

        fluctlight_cursor = fluctlight_client["light-cube-info"]
        active_logs_cursor = fluctlight_client["active_logs"]

        for member in data:
            kick_user = await ctx.guild.fetch_member(member["_id"])

            msg = '\n'.join(rsp["kick"]["kick_all"]) + '\n'
            msg += f'> Levelling index reached {member["lvl_ind"]}.' + '\n'
            msg += '\n'.join(rsp["kick"]["re_join"])
            await kick_user.send(msg)

            try:
                await kick_user.kick(reason=f'Levelling index reached {member["lvl_ind"]}.')
            except Exception as e:
                await ctx.send(f':x: Error when kicking member {member["name"]}({member["_id"]})!')
                await ctx.send(content=e, delete_after=5.0)

            try:
                fluctlight_cursor.delete_one({"_id": member["_id"]})
                active_logs_cursor.delete_one({"_id": member["_id"]})
            except Exception as e:
                await ctx.send(f':x: Error when deleting member {member["name"]}({member["_id"]})\'s fluctlight data!')
                await ctx.send(content=e, delete_after=5.0)

        kick_member_cursor.delete_many({})
        await ctx.send(':white_check_mark: All members in the kick list has been kicked!')


def setup(bot):
    bot.add_cog(Kick_Member(bot))
