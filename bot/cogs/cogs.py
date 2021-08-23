from discord.ext import commands
import os
import sys
import asyncio
from ..core.cog_config import CogExtension
from typing import Tuple


# function for cogs management
def find_cog(bot, target_cog: str, mode: str) -> Tuple[bool, str]:
    def load_ext(full_path: str):
        if mode == 'load':
            bot.load_extension(full_path)
        if mode == 'unload':
            bot.unload_extension(full_path)
        if mode == 'reload':
            bot.reload_extension(full_path)

    for find_filename in os.listdir('./bot/cogs'):
        # normal cog file
        if find_filename.find('.') != -1:
            if find_filename.startswith(target_cog) and find_filename.endswith('.py'):
                load_ext(f'bot.cogs.{find_filename[:-3]}')
                return True, f':white_check_mark: Extension {find_filename} {mode}ed!'
        else:
            for find_sub_filename in os.listdir(f'./bot/cogs/{find_filename}'):
                if find_sub_filename.startswith(target_cog) and find_sub_filename.endswith('.py'):
                    load_ext(f'bot.cogs.{find_filename}.{find_sub_filename[:-3]}')
                    return True, f':white_check_mark: Extension {find_sub_filename} {mode}ed!'
    return False, ''


class Cogs(CogExtension):
    @commands.group()
    @commands.has_any_role('總召', 'Administrator')
    async def cogs(self, ctx):
        pass

    @cogs.command()
    async def load(self, ctx, target_cog: str):
        """cmd
        加載 插件<target_cog>。
        """
        find, msg = find_cog(self.bot, target_cog, 'load')
        if find:
            return await ctx.send(msg)

        return await ctx.send(
            f':exclamation: There are no extension called {target_cog}!'
        )

    @cogs.command()
    async def unload(self, ctx, target_cog: str):
        """cmd
        卸載 插件<target_cog>。
        """
        find, msg = find_cog(self.bot, target_cog, 'unload')
        if find:
            return await ctx.send(msg)

        return await ctx.send(
            f':exclamation: There are no extension called {target_cog}!'
        )

    @cogs.command()
    async def reload(self, ctx, target_cog: str):
        """cmd
        重新加載 插件<target_cog>。
        """
        find, msg = find_cog(self.bot, target_cog, 'reload')
        if find:
            return await ctx.send(msg)

        return await ctx.send(
            f':exclamation: There are no extension called {target_cog}!'
        )

    @commands.command(aliases=['logout', 'shutdown'])
    @commands.has_any_role('總召', 'Administrator')
    async def shut_down(self, ctx):
        """cmd
        安全關閉機器人。
        """
        await ctx.send(':white_check_mark: The bot is shutting down...')
        await self.bot.logout()
        await asyncio.sleep(1)
        sys.exit(0)


def setup(bot):
    bot.add_cog(Cogs(bot))
