from datetime import datetime
from discord.ext import commands
from json import load
from os import listdir
from pymongo import MongoClient


bot = commands.Bot(command_prefix="/")
with open("api.json", "r") as f:
    f = load(f)
    cluster = MongoClient(f.get("mongodb"))
    users = cluster["discord"]["users"]


@bot.event
async def on_ready():
    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded {filename}")
            except commands.ExtensionAlreadyLoaded:
                pass
    print("Bot ready.\n\n")


@bot.event
async def on_member_join(member):
    if not users.find_one({"name": str(member)}):
        users.insert_one({"name": str(member), "level": 1, "xp": 0, "points": 0, "last_time": str(datetime.now())})
    else:
        users.update_one({"name": str(member)}, {"$set": {"level": 1, "xp": 0, "points": 0, "last_time": str(datetime.now())}})


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    elif "logic" == message.content.strip().lower():
        await message.channel.send("buyur")
    elif "sinirimi bozma" in message.content:
        await message.channel.send("hey dostum sakin ol")
    elif "sedat" in message.content.lower():
        await message.channel.send("SEDAAAAAT")
    else:
        users.update_one({"name": str(message.author)}, {"$inc": {"xp": 5}})
        await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"I don't know what `{ctx.message.content.split()[0][1:]}` does!")
        return

    if isinstance(error, commands.CheckFailure) or (isinstance(error, commands.CommandInvokeError) and "Missing Permissions" in str(error)):
        await ctx.send("You don't have the permissions to do this!")
        return

    await ctx.send(f"{error} Type `/help {ctx.message.content.split()[0][1:]}` to learn more about this command.")

    print(f"{datetime.now()} | {ctx.message.author} | \"{ctx.message.content}\" | {error}")

with open("api.json", "r") as f:
    token = load(f).get("discord")

bot.run(token)
