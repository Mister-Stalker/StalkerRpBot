"""
часть бота которая отвечает за команды без граф интерфейса (экипировка и инвентарь)

"""


import pprint
import discord.ext
from discord.ext import commands
from files.scripts.decorators import benchmark, rp_command, rp_command_ping
import files.scripts.items as items
from files.scripts.item_classes import *
from files.scripts.users import Player


class GameCog1(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @rp_command_ping
    @benchmark
    async def inv(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        if len(ctx.message.mentions):
            player = Player(ctx.message.mentions[0].id)
        if "-j" in args:
            await ctx.send(pformat(player.data["inventory"]))
            return
        if "-s" in args:
            text = "инвентарь:\n"
            for i, item in enumerate(player.data["inventory"]):
                item_d = items.get_info_for_tpl(item["tpl"])
                print(item_d)
                if item_d["stackable"]:
                    text += f'{i + 1}: {item_d["name"]} x{item["StackObjectsCount"]}\n'
                else:
                    text += f'{i+1}: {item_d["name"]}\n'

            await ctx.send(text)
            return
        else:
            text = "инвентарь:\n"
            for i, item in enumerate(player.data["inventory"]):
                item_d = items.get_info_for_tpl(item["tpl"])
                print(item_d)
                if item_d["stackable"]:
                    text += f'{i + 1}: {item_d["name"]} x{item["StackObjectsCount"]}\n'
                elif item_d["type"] == "magazine":
                    mag = items.Item(item["_id"])

                    text += f'{i + 1}: {item_d["name"]} {mag["data"]["ammo_count"]}/' \
                            f'{item_d["parameters"]["mag_size"]}, ' \
                            f'{get_info_for_tpl(mag["data"]["ammo_type"])["name"][7:]}\n'
                else:
                    text += f'{i + 1}: {item_d["name"]}\n'
            await ctx.send(text)

    @commands.command(aliases=["b"])
    @benchmark
    @rp_command
    async def belt(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        if "-j" in args:
            belt = Belts(player)
            j = {}
            for slot in belt["data"]["belt"]:
                item_obj = belt["data"]["belt"][slot]
                if item_obj:
                    j[slot] = items.Item(item_obj["_id"]).data
                else:
                    j[slot] = ""
            await ctx.send(pprint.pformat(j))
        elif "-t" in args:
            belt = Belts(player)
            text = f"{ctx.author.nick} Разгрузка: {belt.get_configs()['name']}\n"

            for slot in belt.get_configs()["data"]["belt"]:
                item_obj = belt["data"]["belt"][slot]
                if item_obj:
                    item = items.Item(item_obj["_id"])
                    text += f"слот {slot}: {item.get_configs()['name']}, "\
                            f"{item['data']['ammo_count']}/{item.get_configs()['parameters']['mag_size']}, "\
                            f"{get_info_for_tpl(item['data']['ammo_type'])['name'][7:]}\n"
                else:
                    text += f"слот {slot}: пуст\n"
            await ctx.send(text)
        else:
            belt = Belts(player)
            embed = discord.Embed(title=f"{ctx.author.name} Разгрузка:",
                                  description=belt.get_configs()["name"], color=0xfad000)
            for slot in belt.get_configs()["data"]["belt"]:
                item_obj = belt["data"]["belt"][slot]
                if item_obj:
                    item = items.Item(item_obj["_id"])
                    embed.add_field(name=f"слот {slot}",
                                    value=f"{item.get_configs()['name']}, "
                                    f"{item['data']['ammo_count']}/{item.get_configs()['parameters']['mag_size']}, "
                                    f"{get_info_for_tpl(item['data']['ammo_type'])['name'][7:]}", inline=False)
                else:
                    embed.add_field(name=f"слот {slot}", value="пуст", inline=False)
            await ctx.send(embed=embed)

    @commands.command(aliases=["ue", "снять"])
    @benchmark
    @rp_command
    async def takeoff(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        belt = Belts(player)
        if args[0] in belt.get_configs()["parameters"]["belt"]["associate_keys"].keys():
            key = belt.get_configs()["parameters"]["belt"]["associate_keys"][args[0]]
            if belt["data"]["belt"][key]:
                player.add_to_inventory(belt["data"]["belt"][key])
                belt.update(f'data.belt.{key}', {})
        if args[0].isdigit():
            if int(args[0]) in range(1, 7):
                item = player["equipment"][f"slot_{args[0]}"]
                if item:
                    player.update(f"equipment.slot_{args[0]}", {})
                    player.add_to_inventory(item)

    @commands.command(aliases=["экипировать", "eq"])
    @benchmark
    @rp_command
    async def equip(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        item = items.Item(player["inventory"][int(args[0]) - 1]["_id"])
        item_obj = player["inventory"][int(args[0]) - 1]
        if item.get_type() in ["magazine"]:
            if len(args) == 1:
                pass
            else:
                slot = args[1]
                belt = Belts(player)
                if slot in belt.get_configs()["parameters"]["belt"]["associate_keys"].keys():
                    slot = belt.get_configs()["parameters"]["belt"]["associate_keys"][slot]
                    if slot[0] in item.get_configs()["parameters"]["slots"]:
                        old_mag = belt["data"]["belt"][slot]
                        if old_mag:
                            player.add_to_inventory(old_mag)
                        belt.update(f"data.belt.{slot}", item_obj)
                        player.remove_from_inventory(item_obj["_id"])
                    else:
                        pass
        elif item.get_type() in ["belt", "weapon","armor"]:
            if len(args) == 1:
                slot = item.get_configs()["parameters"]["slots"][0]
            elif not args[1].isdigit():
                pass
                return
            else:
                slot = f"slot_{args[1]}"
                if not slot in item.get_configs()["parameters"]["slots"]:
                    slot = item.get_configs()["parameters"]["slots"][0]
            if player["equipment"][slot]:
                player.add_to_inventory(player["equipment"][slot])
            player.remove_from_inventory(item_obj["_id"])
            player.update(f"equipment.{slot}", item_obj)

    @commands.command(aliases=["g_экипировать", "ge"])
    @benchmark
    @rp_command
    async def g_equip(self, ctx: discord.ext.commands.context.Context, *args):
        pass

    @commands.command(aliases=["оружие"])
    @benchmark
    @rp_command
    async def weapon(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        if "-j" in args:
            slot = player["equipment"]["active_weapon"]
            item = items.Item(player["equipment"][slot]["_id"])
            print(item.data)
            await ctx.send(pprint.pformat(item.data))

    @commands.command(aliases=["перезарядить", "р", "r"])
    @benchmark
    @rp_command
    async def reload(self, ctx: discord.ext.commands.context.Context, *args):
        args = list(args)
        flags = []
        if "-u" in args:
            flags.append("-u")
            del args[args.index("-u")]
        player = Player(ctx.author.id)
        belt = Belts(player)
        if len(args) == 0:  # если ничего нет
            weapon = Weapons(player, player["equipment"][player["equipment"]["active_weapon"]]["_id"])
            r = weapon.reload()
            print(r)
        elif "-f" in args:
            pass
        elif args[0] in belt["data"]["belt"].keys() and len(args) == 1:
            weapon = Weapons(player, player["equipment"][player["equipment"]["active_weapon"]]["_id"])
            r = weapon.reload_r_slot(args[0])
            print(r)
        elif args[0].isdigit() and len(args) == 1:
            weapon = Weapons(player, player["equipment"][player["equipment"]["active_weapon"]]["_id"])
            r = weapon.reload_inv_slot(int(args[0])-1)
            print(r)
        elif args[0].isdigit() and args[1].isdigit():
            print(items.associate[player["inventory"][int(args[0])-1]["tpl"]])
            if items.associate[player["inventory"][int(args[0])-1]["tpl"]] == "magazine":
                magazine = Magazines(player, player["inventory"][int(args[0])-1]["_id"])
                r = magazine.reload(int(args[1])-1)
                print(r)
        elif args[0] in belt["data"]["belt"].keys() and args[1].isdigit():
            if True:
                magazine = Magazines(player, belt["data"]["belt"][args[0]]["_id"])
                r = magazine.reload(int(args[1])-1)
                print(r)


def setup(bot):
    bot.add_cog(GameCog1(bot))
