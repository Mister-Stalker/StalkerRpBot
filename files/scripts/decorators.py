import pymongo
import functools
import time
from files.scripts.users import Player


def benchmark(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        await func(*args, **kwargs)
        print(f"[BENCHMARK] функция {func} {time.time()- start}")
    return wrapper


def get_db_for_commands(func):
    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        client = pymongo.MongoClient('localhost', 27017)
        db_name = "users"
        db = client["stalker_rp"]
        await func(self, ctx, db[db_name], *args, **kwargs)

    return wrapper


def rp_command(func):
    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        user = Player(ctx.author.id)
        # print("decor", self, ctx, args, kwargs, sep='\n')
        # print(user.is_reg)
        if not user.is_reg:
            await ctx.send(f'{ctx.author.mention} не является участником')
            return
        await func(self, ctx, *args, **kwargs)
    return wrapper


def rp_command_ping(func):
    @functools.wraps(func)
    async def wrapper(self, ctx, *args, **kwargs):
        user = Player(ctx.author.id)
        if len(ctx.message.mentions):
            user = Player(ctx.message.mentions[0].id)
            if not user.is_reg:
                await ctx.send(f'{ctx.message.mentions[0].mention} не является участником')
                return
        if not user.is_reg:
            await ctx.send(f'{ctx.author.mention} не является участником')
            return
        await func(self, ctx, user, *args, **kwargs)

    return wrapper



def get_db_for_commands_db(arg="users"):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, ctx, *args, **kwargs):
            client = pymongo.MongoClient('localhost', 27017)
            db = client["stalker_rp"]
            
            await func(self, ctx, db[arg], *args, **kwargs)
        return wrapper
    return decorator
