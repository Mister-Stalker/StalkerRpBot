import json

from discord.ext import commands
import discord
bot = commands.Bot(command_prefix=commands.when_mentioned_or('-'), case_insensitive=True, intents=discord.Intents.all())
bot.load_extension('Extensions.system')
bot.load_extension('Extensions.game_1')
bot.load_extension('Extensions.game_2')
bot.load_extension('Extensions.game_3')


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
async def on_ready():
    for channel in bot.get_guild(935971436131156088).channels:
        print(channel, channel.id)
    print("бот запущен и готов к работе")


@bot.command()
async def logout(ctx):
    await ctx.send(f"отключение бота")
    await bot.logout()


@bot.command(aliases=["запинговать"])
async def pinggg(ctx, user, num: int, *, arg=""):
    if num > 25:
        await ctx.send(f"{ctx.message.author.mention} ограничение 25!!!!!")
        return
    for i in range(num):
        await ctx.send(f"{user} {arg}")


while True:
    bot.run(json.load(open("bot_configs.json"))["token"])
