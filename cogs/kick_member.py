from pymongo import MongoClient
from core.classes import Cog_Extension
from discord.ext import commands
from core.setup import jdata, client, link
import core.functions as func
import discord
import asyncio
import random
import json
import pymongo
import core.score_module as sm

class Kick_Member(Cog_Extension):

    @commands.group()
    async def kick(self, ctx):
        pass

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def list(self, ctx):
        kick_member_cursor = client["kick_member_list"]

        kick_member_list = str()
        data = kick_member_cursor.find({})

        if data is None:
            await ctx.send('There are no member in the kick list!')
            return

        for member in data:
            kick_member_list += f'Id: {member["_id"]}, Name: {member["name"]}, Contrib: {member["contrib"]}, lvl_ind: {member["lvl_ind"]}\n'

            if len(kick_member_list) >= 1800:
                await ctx.send(kick_member_list)
                kick_member_list = ''

        if len(kick_member_list) > 0:
            await ctx.send(kick_member_list)

        await ctx.send('Logging finished!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group kick - list used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def add(self, ctx, member_id: int):
        fluctlight_client = MongoClient(link)["LightCube"]
        fluctlight_cursor = fluctlight_client["light-cube-info"]

        data = fluctlight_cursor.find_one({"_id": member_id}, {"contrib": 1, "lvl_ind": 1})

        if data is None:
            await ctx.send(f'There\'re no data of member whose id is {member_id}')
            return

        member_contrib = data["contrib"]
        member_lvl_ind = data["lvl_ind"]

        member = await self.bot.guilds[0].fetch_member(member_id)
        member_name = member.nick
        if member_name is None:
            member_name = member.name

        member_info = {"_id": member_id, "name": member_name, "contrib": member_contrib, "lvl_ind": member_lvl_ind}

        kick_member_cursor = client["kick_member_list"]
        kick_member_cursor.insert_one(member_info)

        await ctx.send(f'Member {member_name}({member_id}) has been added to the kick list!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group kick - add used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def remove(self, ctx, member_id: int):
        kick_member_cursor = client["kick_member_list"]
        data = kick_member_cursor.find_one({"_id": member_id})

        if data is None:
            await ctx.send(f'Member {member_id} isn\'t in the kick list!')
            return

        kick_member_cursor.delete_one({"_id": member_id})

        await ctx.send(f'Member {member_id} has been removed from the kick list!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group kick - remove used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def kick_single(self, ctx, member_id: int, reason: str):
        kick_member_cursor = client["kick_member_list"]
        data = kick_member_cursor.find_one({"_id": member_id})

        if data is None:
            await ctx.send(f'Member {member_id} isn\'t in the kick list!')
            return

        kick_user = await ctx.guild.fetch_member(member_id)

        if reason == 'default':
            kick_reason = f'Levelling index reached {data["lvl_ind"]}.'
        else:
            kick_reason = reason

        await kick_user.kick(reason=kick_reason)

        fluctlight_client = MongoClient(link)["LightCube"]
        fluctlight_cursor = fluctlight_client["light-cube-info"]
        active_logs_cursor = fluctlight_client["active_logs"]

        try:
            kick_member_cursor.delete_one({"_id": member_id})
            fluctlight_cursor.delete_one({"_id": member_id})
            active_logs_cursor.delete_one({"_id": member_id})
        except:
            pass

        await ctx.send(f'Kicked member {data["name"]}({data["_id"]})!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group kick - kick_single used by member {ctx.author.id}. {func.now_time_info("whole")}')

    @kick.command()
    @commands.has_any_role('總召', 'Administrator')
    async def kick_all(self, ctx):
        kick_member_cursor = client["kick_member_list"]

        data = kick_member_cursor.find({})

        if data is None:
            await ctx.send('Kick member list is empty!')
            return

        fluctlight_client = MongoClient(link)["LightCube"]
        fluctlight_cursor = fluctlight_client["light-cube-info"]
        active_logs_cursor = fluctlight_client["active_logs"]

        for member in data:
            kick_user = await ctx.guild.fetch_member(member["_id"])
            await kick_user.kick(reason=f'Levelling index reached {member["lvl_ind"]}.')

            try:
                fluctlight_cursor.delete_one({"_id": member["_id"]})
                active_logs_cursor.delete_one({"_id": member["_id"]})
            except:
                pass

        kick_member_cursor.delete_many({})
        await ctx.send('All members in the kick list has been kicked!')

        await func.getChannel(self.bot, '_Report').send(
            f'[Command]Group kick - kick_all used by member {ctx.author.id}. {func.now_time_info("whole")}')


def setup(bot):
    bot.add_cog(Kick_Member(bot))