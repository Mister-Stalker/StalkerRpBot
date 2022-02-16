"""
часть бота которая отвечает за обработку событий on_message (для нпс)

"""
import random

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
        print("[DEBUG] on message from GameCog3:\n", mess, '\n', type(mess))
        if mess.author.bot:
            return
        if mess.content == "...":
            await mess.channel.send("...")
        location = Locations(_id=mess.channel.id)
        if not location.rp:
            return
        r = random.randint(0, 100)
        if mess.content[:3] == "npc" or r < 10:
            # npc attack or do
            pass
            print("npc_attack")


    @commands.command(aliases=["ac"])
    async def add_channel(self, ctx: discord.ext.commands.Context, name=None, rp="rp"):
        create_channel(ctx.channel.id, name, rp)
        location = Locations(ctx.channel.id)
        print(location.info)


def setup(bot):
    bot.add_cog(GameCog3(bot))
