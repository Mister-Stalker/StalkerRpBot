import json

from discord.ext import commands
import discord
bot = commands.Bot(command_prefix='-', case_insensitive=True, intents=discord.Intents.all())
bot.load_extension('Extensions.system')
@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is ratelimited, please try again in {error.retry_after}s')
        await ctx.message.delete(delay=1)
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        raise error


@bot.event
async def on_ready(): print("бот запущен и готов к работе")


@bot.command()
async def logout(ctx):
    await ctx.send(f"{ctx.message.author.mention} я уми....")
    await bot.logout()


@bot.command(aliases=["запинговать"])
async def pinggg(ctx, user, num: int, *, arg=""):
    if num > 25:
        await ctx.send(f"{ctx.message.author.mention} ограничение 25!!!!!")
        return
    for i in range(num):
        await ctx.send(f"{user} {arg}")


"""https://discord.gg/fpCVqBQK"""
while True:
    bot.run(json.load(open("bot_configs.json"))["token"])


