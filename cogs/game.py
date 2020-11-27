from datetime import datetime
from discord import Client, Embed, Member
from discord.ext import commands
from json import load
from math import log
from pymongo import MongoClient
from random import choice


class Game(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        with open("api.json", "r") as f:
            f = load(f)
            cluster = MongoClient(f.get("mongodb"))
            self.users = cluster["discord"]["users"]

    async def update(self, username: str):
        if not self.users.find_one({"name": username}):
            self.users.insert_one({"name": username, "level": 1, "xp": 0, "points": 0, "last_time": str(datetime.now())})
        if "level" not in self.users.find_one({"name": username}).keys():
            self.users.update_one({"name": username},
                                  {"$set": {"level": 1, "xp": 0, "points": 0, "last_time": str(datetime.now())}})

        user = self.users.find_one({"name": username})
        time_diff = int((datetime.now() - datetime.fromisoformat(user["last_time"])).total_seconds() / 432)
        new_xp = user["xp"] + time_diff
        new_points = user["points"] + time_diff
        new_level = int(new_xp / 142.85) if new_xp < 10000 else int(log(new_xp) / log(1.14))
        self.users.update_one({"name": username},
                              {"$set": {"level": new_level, "xp": new_xp, "points": new_points, "last_time": str(datetime.now())}})
        return new_xp, new_points, new_level

    @commands.command()
    async def level(self, ctx: commands.Context):
        new_xp, new_points, new_level = await self.update(str(ctx.author))
        required_xp = int((new_level+1) * 142.85) if new_level < 70 else int(pow(1.14, new_level+1))

        embed = Embed(title=f"{ctx.author.display_name}'s Level", color=0xf1c40f)
        embed.add_field(name="\u200b", value=f"Level: {new_level}\nXP: {new_xp}/{required_xp}\nPoints: {new_points}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["leaderboards"])
    async def leaderboard(self, ctx: commands.Context):
        embed = Embed(title="HisarCS Leaderboard", color=0x7289da)
        embed_txt = ""

        # This might take a while
        for user in self.users.find():
            await self.update(user["name"])

        for i, user_str in enumerate([user["name"][:-5] + ": " + str(user["xp"]) for user in sorted(self.users.find(), key=lambda x: x["xp"], reverse=True)][0:5], start=1):
            embed_txt += f"{i}. {user_str}\n"

        embed.add_field(name="\u200b", value=embed_txt[:-1])
        await ctx.send(embed=embed)

    @commands.command()
    async def gamble(self, ctx: commands.Context, amount: int):
        await self.update(str(ctx.author))
        user = self.users.find_one({"name": str(ctx.author)})
        if user["points"] < amount:
            await ctx.send(f"You don't have {amount} points!")
            return

        if choice([0, 1]):
            self.users.update_one({"name": str(ctx.author)}, {"$inc": {"points": -amount}})
            await ctx.send(f"You lost {amount} points!")
        else:
            self.users.update_one({"name": str(ctx.author)}, {"$inc": {"xp": amount, "points": amount}})
            await ctx.send(f"You won {amount} points!")

    @commands.command()
    async def give(self, ctx: commands.Context, target: Member, amount: int):
        # Update the authors and targets points first
        await self.update(str(ctx.author))
        await self.update(str(target))

        if self.users.find_one({"name": str(ctx.author)})["points"] < amount:
            await ctx.send(f"You don't have {amount} points!")
            return

        self.users.update_one({"name": str(ctx.author)}, {"$inc": {"points": -amount}})
        self.users.update_one({"name": str(target)}, {"$inc": {"points": amount}})
        await ctx.send(f"{ctx.author.display_name} gave {amount} points to {target.mention}!")


def setup(client: Client):
    client.add_cog(Game(client))
