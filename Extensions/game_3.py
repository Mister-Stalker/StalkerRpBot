"""
часть бота которая отвечает за обработку событий on_message (для нпс)

"""

import discord.ext
from discord.ext import commands
from discord import Button, ButtonStyle, SelectMenu, SelectOption

import pprint
from files.scripts.decorators import benchmark, rp_command, rp_command_ping
import files.scripts.items as items
from files.scripts.item_classes import *
from files.scripts.locations import create_channel, Locations

class GameCog3(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, mess: discord.Message):
        print(mess, '\n', type(mess))
        if mess.author.bot:
            return
        if mess.content == "...":
            await mess.channel.send("...")

    @commands.command(aliases=["ac"])
    async def add_channel(self, ctx: discord.ext.commands.Context, name=None, rp="rp"):
        create_channel(ctx.channel.id, name, rp)
        l = Locations(ctx.channel.id)
        print(l.info)


def setup(bot):
    bot.add_cog(GameCog3(bot))
