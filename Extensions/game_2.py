"""
часть бота которая отвечает за команды с графическим интерфейсом (экипировка)

"""


import discord.ext
from discord.ext import commands
from discord import Button, ButtonStyle, SelectMenu, SelectOption

import pprint
from files.scripts.decorators import benchmark, rp_command, rp_command_ping
import files.scripts.items as items
from files.scripts.item_classes import *


class GameCog2(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def buttons(self, ctx):
        msg_with_buttons = await ctx.send('Hey here are some Buttons', components=[[
            Button(label="Hey i\'m a red Button",
                   custom_id="red",
                   style=ButtonStyle.red),
            Button(label="Hey i\'m a green Button",
                   custom_id="green",
                   style=ButtonStyle.green),
            Button(label="Hey i\'m a blue Button",
                   custom_id="blue",
                   style=ButtonStyle.blurple),
            Button(label="Hey i\'m a grey Button",
                   custom_id="grey",
                   style=ButtonStyle.grey)
        ]])

        def check_button(i, *args):
            print("aboba")
            return i.author == ctx.author and i.message == msg_with_buttons

        interaction, button = await self.bot.wait_for('button_click', check=check_button)

        embed = discord.Embed(title='You pressed an Button',
                              description=f'You pressed a {button.custom_id} button.',
                              color=discord.Color.random())
        await interaction.respond(embed=embed)

    @commands.command()
    async def select(self, ctx):
        msg_with_selects = await ctx.send('Hey here is an nice Select-Menu', components=[
            [
                SelectMenu(custom_id='_select_it', options=[
                    SelectOption(emoji='1️⃣', label='Option Nr° 1', value='1', description='The first option'),
                    SelectOption(emoji='2️⃣', label='Option Nr° 2', value='2', description='The second option'),
                    SelectOption(emoji='3️⃣', label='Option Nr° 3', value='3', description='The third option'),
                    SelectOption(emoji='4️⃣', label='Option Nr° 4', value='4', description='The fourth option')],
                           placeholder='Select some Options', max_values=3)
            ]])

        def check_selection(i: discord.Interaction, select_menu):
            return i.author == ctx.author and i.message == msg_with_selects

        interaction, select_menu = await self.bot.wait_for('selection_select', check=check_selection)

        embed = discord.Embed(title='You have chosen:',
                              description=f"You have chosen " + '\n'.join(
                                  [f'\nOption Nr° {o}' for o in select_menu.values]),
                              color=discord.Color.random())
        await interaction.respond(embed=embed)

    async def equip_gui_mag(self, ctx, interaction):
        user = User(ctx.author.id)
        select_menu_list = []
        flag = False
        for i, item_obj in enumerate(user["inventory"]):
            if not item_obj["stackable"]:
                item = Item(item_obj["_id"])
                if item.info["type"] in ["magazine"]:
                    flag = True
                    select_menu_list.append(SelectOption(label=item.info["name"], value=str(i),
                                                         description=f"{item['data']['ammo_count']}/{item.info['parameters']['mag_size']}, {get_info_for_tpl(item['data']['ammo_type'])['name']}"))
                
        if not flag:
            return
        
        sm = SelectMenu(custom_id='_select_it', options=select_menu_list,
                        placeholder='Select some Options', max_values=1)
        msg_with_menu = await interaction.respond('выбирете предмет который хотите экипировать', components=[[sm], [
                            Button(label="Hey i\'m a red Button", custom_id="red", style=ButtonStyle.red)]])

        def check_selection(i: discord.Interaction, select_menu):
            return i.author == ctx.author and i.message == msg_with_menu
        interaction_2, select_menu = await self.bot.wait_for('selection_select', check=check_selection)
        mag_id = select_menu.values[0]
        user = User(interaction_2.author.id)
        mag_obj = user["inventory"][mag_id]
        mag = items.Item(mag_obj["_tpl"])
        
        
    async def equip_gui_v2(self, ctx):
        
        msg_with_buttons = await ctx.send('select the type of item', components=[[
            Button(label="Оружие",
                   custom_id="weapon",
                   style=ButtonStyle.green),
            Button(label="Броня",
                   custom_id="armor",
                   style=ButtonStyle.green),
            Button(label="Магазин",
                   custom_id="mag",
                   style=ButtonStyle.green),
            Button(label="Разгрузка",
                   custom_id="belt",
                   style=ButtonStyle.green)
        ]])

        def check_button(i, *args):
            return i.author == ctx.author and i.message == msg_with_buttons

        interaction, button = await self.bot.wait_for('button_click', check=check_button)
        
        if button.custom_id == "mag":
            await self.equip_gui_mag(ctx, interaction)

    async def equip_gui(self, ctx):
        user = User(ctx.author.id)
        select_menu_list = []
        for i, item_obj in enumerate(user["inventory"]):
            if not item_obj["stackable"]:
                item = Item(item_obj["_id"])
                if item.info["type"] in ["magazine"]:
                    select_menu_list.append(SelectOption(label=item.info["name"], value=str(i),
                                                         description=f"{item['data']['ammo_count']}/{item.info['parameters']['mag_size']}, {get_info_for_tpl(item['data']['ammo_type'])['name']}"))
                else:
                    select_menu_list.append(SelectOption(label=item.info["name"], value=str(i)))

        sm = SelectMenu(custom_id='_select_it', options=select_menu_list,
                        placeholder='Select some Options', max_values=1)
        msg_with_menu = await ctx.send('выбирете предмет который хотите экипировать', components=[[sm], [
                            Button(label="Hey i\'m a red Button", custom_id="red", style=ButtonStyle.red)]])

        def check_selection(i: discord.Interaction, select_menu):
            return i.author == ctx.author and i.message == msg_with_menu

    @commands.command()
    @rp_command
    async def e(self, ctx: discord.ext.commands.context.Context, *args):
        if "-t" in args:
            pass
        else:
            await self.equip_gui(ctx)


def setup(bot):
    bot.add_cog(GameCog2(bot))
