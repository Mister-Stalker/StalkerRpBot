import json
import os
import pprint

import bson
import discord.ext.commands
from discord.ext import commands
from files.scripts.users import Player
from files.configs.items.associate_type import associate
import files.scripts.items as items
from files.scripts.decorators import get_db_for_commands_db, benchmark, rp_command


class SystemCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["пинг"])
    async def ping(self, ctx):
        print(type(ctx))
        ping = self.bot.latency
        ping = round(ping * 1000)
        await ctx.send(f"my ping is {ping}ms")

    @commands.command()
    async def descr(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        if len(args) < 1:
            return
        n = int(args[0])
        if n > len(player.data["inventory"]):
            return
        n -= 1
        if "-j" in args:
            await ctx.send(player.data["inventory"][n])
            return
        data = items.get_info_for_tpl(player.data["inventory"][n]["tpl"])
        await ctx.send(f'{data["name"]}\n{data["description"]}')

    @commands.command()
    @rp_command
    async def stats(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        # print("command", self, ctx, args, user, sep='\n')
        if "-j" in args:
            await ctx.send(pprint.pformat(player.data ))
            return
        await ctx.send(f"""id: {player["id"]}\nhealth: {player["health"]["current"]}/{player["health"]["maximum"]}""")

    @commands.command()
    @get_db_for_commands_db("users")
    async def new(self, ctx: discord.ext.commands.context.Context, db=None, *args):
        new_user_json = json.load(open(str(os.getcwd()) + f"\\files\\configs\\profile_mask.json"))
        new_user_json["id"] = ctx.author.id
        new_user_json["nickname"] = ctx.author.nick
        res = db.insert_one(new_user_json)
        await ctx.send(str(res)+str(new_user_json))

    @commands.command(aliases=["d"])
    async def dev(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        if "-r" in args:
            i = int(args[args.index("-r") + 1])
            item = player["inventory"][i-1]
            count = 1
            if "-c" in args:
                count = int(args[args.index("-c") + 1])
            if items.get_info_for_tpl(item["tpl"])["stackable"]:
                player.remove_from_inventory_stackable(item["tpl"], count)
            else:
                player.remove_from_inventory(item["_id"])
        if "-g" in args:
            i = int(args[args.index("-g") + 1])
            item = player["inventory"][i-1]
            data = []
            if items.get_info_for_tpl(item["tpl"])["stackable"]:
                data = player.get_from_inventory_stackable(item["tpl"])
            else:
                data = player.get_from_inventory(item["_id"])
            pprint.pprint(data)
            await ctx.send(data)

    @commands.command(aliases=["s"])
    async def spawn_item(self, ctx, tpl, *args):
        repeat = 1

        if "-r" in args:
            repeat = args[args.index("-r")+1]
        print(repeat)
        for i in range(int(repeat)):
            player = Player(ctx.author.id)
            if items.get_info_for_tpl(tpl)["stackable"]:
                num = 1
                if len(args) >= 1 and args[0].isdigit():
                    num = int(args[0])
                print(num)
                player.add_to_inventory_stackable(tpl, num)
            else:
                item_id, item = items.create_empty_item(tpl)
                player.add_to_inventory(item)
        print("done")

    @commands.command()
    @rp_command
    async def info(self, ctx: discord.ext.commands.context.Context, *args):
        player = Player(ctx.author.id)
        if args[0][:4] == "slot":
            item = items.Item(player["equipment"][args[0]]["_id"])
            await ctx.send(pprint.pformat(item.data))
        else:
            if player["inventory"][int(args[0])-1]["stackable"]:
                await ctx.send(pprint.pformat(player["inventory"][int(args[0]) - 1]))
            else:
                await ctx.send(pprint.pformat(items.Item(player["inventory"][int(args[0])-1]["_id"]).data))

    @commands.command()
    @rp_command
    async def id(self, ctx: discord.ext.commands.context.Context, *args):
        await ctx.send(pprint.pformat(items.Item(bson.ObjectId(args[0])).data))


def setup(bot):
    bot.add_cog(SystemCog(bot))
