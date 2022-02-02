import json
import os
import discord.ext.commands
from discord.ext import commands
from files.scripts.users import User
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
        user = User(ctx.author.id)
        if len(args) < 1:
            return
        n = int(args[0])
        if n > len(user.data["inventory"]):
            return
        n -= 1
        if "-j" in args:
            await ctx.send(user.data["inventory"][n])
            return
        data = items.get_info_for_tpl(user.data["inventory"][n]["tpl"])
        await ctx.send(f'{data["name"]}\n{data["description"]}')

    @commands.command()
    async def inv(self, ctx: discord.ext.commands.context.Context, *args):
        user = User(ctx.author.id)
        if len(ctx.message.mentions):
            user = User(ctx.message.mentions[0].id)
        if "-j" in args:
            await ctx.send(user.data["inventory"])
            return
        if len(args) == 0:
            text = "инвентарь:\n"
            for i, item in enumerate(user.data["inventory"]):
                item_d = items.get_info_for_tpl(item["tpl"])
                print(item_d)
                if item_d["stackable"]:
                    text += f'{i + 1}: {item_d["name"]} x{item["StackObjectsCount"]}\n'
                else:
                    text += f'{i+1}: {item_d["name"]}\n'

            await ctx.send(text)

    @commands.command()
    @rp_command
    async def stats(self, ctx: discord.ext.commands.context.Context, *args):
        user = User(ctx.author.id)
        # print("command", self, ctx, args, user, sep='\n')
        if "-j" in args:
            await ctx.send(user.data)
            return
        await ctx.send(f"""id: {user["id"]}\nhealth: {user["health"]["current"]}/{user["health"]["maximum"]}""")

    @commands.command()
    @get_db_for_commands_db("users")
    async def new(self, ctx: discord.ext.commands.context.Context, db=None, *args):
        new_user_json = json.load(open(str(os.getcwd()) + f"\\server\\profile_mask.json"))
        new_user_json["id"] = ctx.author.id
        new_user_json["nickname"] = ctx.author.nick
        res = db.insert_one(new_user_json)
        await ctx.send(str(res)+str(new_user_json))

    @commands.command(aliases=["s"])
    async def spawn_item(self, ctx, tpl, *args):
        repeat = 1
        if "-r" in args:
            repeat = args[args.index("-r")+1]
        print(repeat)
        for i in range(int(repeat)):
            user = User(ctx.author.id)
            if items.get_info_for_tpl["stackable"]:
                num = 1
                if len(args)>=2 and args[1].isdigit():
                    num = int(args[1])
                user.add_to_inventory_stackable(tpl, num)
            else:
                item_id, item = items.create_empty_item(tpl)
                user.add_to_inventory(item)
        print("done")


def setup(bot):
    bot.add_cog(SystemCog(bot))
