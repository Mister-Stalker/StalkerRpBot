import pprint

import discord.ext
from discord.ext import commands
from files.scripts.decorators import benchmark, rp_command
# import pprint
from files.scripts.users import User
# from files.configs.items.associate_type import associate
import files.scripts.items as items


class GameCog1(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["экипировать"])
    @benchmark
    @rp_command
    async def equip(self, ctx: discord.ext.commands.context.Context, *args):
        user = User(ctx.author.id)
        item = items.Item(user["inventory"][int(args[0]) - 1]["_id"])
        item_obj = user["inventory"][int(args[0]) - 1]
        if item.get_type() in ["belt", "weapon"]:
            if len(args) == 1:
                slot = item.get_configs()["parameters"]["slots"][0]
            else:
                slot = f"slot_{args[1]}"
                if not slot in item.get_configs()["parameters"]["slots"]:
                    slot = item.get_configs()["parameters"]["slots"][0]
            if user["equipment"][slot]:
                user.add_to_inventory(user["equipment"][slot])
            user.remove_from_inventory(item_obj["_id"])
            user.update(f"equipment.{slot}", item_obj)

    @commands.command(aliases=["оружие"])
    @benchmark
    @rp_command
    async def weapon(self, ctx: discord.ext.commands.context.Context, *args):
        user = User(ctx.author.id)
        if "-j" in args:
            slot = user["equipment"]["active_weapon"]
            item = items.Item(user["equipment"][slot]["_id"])
            print(item.data)
            await ctx.send(pprint.pformat(item.data))


def setup(bot):
    bot.add_cog(GameCog1(bot))
