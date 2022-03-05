"""
часть бота которая отвечает за обработку переходов по локациям и взамимодействие с нпс

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
        pass

    @commands.command(aliases=["перейти"])
    @rp_command
    async def go(self, ctx: discord.ext.commands.Context):
        user = Player(ctx.author.id)
        location = Locations(ctx.channel.id)
        tree = location.get_tree_channels()
        print(tree, location.rp)
        if not location.rp:
            return
        if not tree:
            return
        select_menu_list = []
        for i, loc in enumerate(tree):
            select_menu_list.append(SelectOption(label=loc[0], value=loc[0]))
        sm = SelectMenu(custom_id='_select_location', options=select_menu_list,
                        placeholder='Select some Options', max_values=1)
        msg_with_menu = await ctx.send('выбирете location', components=[[sm]])

        def check_selection(i: discord.Interaction, select_menu):
            return i.author == ctx.author and i.message == msg_with_menu
        interaction, select_menu = await self.bot.wait_for('selection_select', check=check_selection)

        sm_list = select_menu.values
        print(sm_list)
        new_location = Locations(name=sm_list[0])
        user.update("location", new_location.name)
        embed = discord.Embed(title='You have chosen:',
                              description=f"You have chosen {new_location.name}",
                              color=discord.Color.random())
        await interaction.respond(embed=embed)

        await ctx.channel.set_permissions(ctx.author, view_channel=False)

        new_channel = self.bot.get_channel(int(new_location.info["id"]))
        await new_channel.set_permissions(ctx.author, view_channel=True)

    @commands.command(aliases=["a"])
    @rp_command
    async def attack(self, ctx: discord.ext.commands.Context, *args):
        print("attack")
        opponent = Player(ctx.message.mentions[0].id)
        player = Player(ctx.author.id)
        r = await player.attack(opponent, shoot_type="2")
        print("attack r:", r)



def setup(bot):
    bot.add_cog(GameCog3(bot))
