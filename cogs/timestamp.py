from datetime import datetime, timedelta
from discord import Client, Embed, Role
from discord.ext import commands, tasks
from json import load
from praw import Reddit
from pymongo import MongoClient


class Timestamp(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        with open("api.json", "r") as f:
            f = load(f)
            cluster = MongoClient(f.get("mongodb"))
            self.meetings = cluster["timestamp"]["meeting"]
            self.subreddits = cluster["timestamp"]["reddit"]
            self.praw = Reddit(client_id=f.get("reddit_id"), client_secret=f.get("reddit_secret"), user_agent="-")

    @commands.command()
    async def meeting(self, ctx: commands.Context, role: Role, amount: int, s: str):
        if s[-1] == "s":
            s = s[:-1]
        time_dict = {"month": 10080, "day": 1440, "hour": 60, "minute": 1}
        meeting_time = datetime.now()+timedelta(minutes=amount*time_dict[s])
        self.meetings.insert_one({"role": role.mention, "meeting_time": meeting_time, "channel": ctx.channel.id})
        await ctx.send(f"The meeting for `{role.name}` will be in {meeting_time.strftime('%d-%m-%Y %H:%M:%S')}")

    @tasks.loop(minutes=1.0, count=None)
    async def meeting_check(self):
        meeting_alerts = self.meetings.find({"meeting_time": {"$lt": datetime.now(), "$gt": datetime.now()-timedelta(minutes=5)}})
        for meeting in meeting_alerts:
            await self.client.get_channel(meeting["channel"]).send(f"Meeting time for {meeting['role']}!")
            self.meetings.delete_one({"meeting_time": meeting["meeting_time"]})

    @tasks.loop(hours=1.0, count=None)
    async def reddit_check(self):
        subreddits_to_post = self.subreddits.find({"last_checked": {"$lt": datetime.now()-timedelta(days=1)}})
        for subreddit in subreddits_to_post:
            posts = self.praw.subreddit(subreddit["name"]).top("day", limit=5)
            for post in posts:
                if post.score > 1000:
                    embed = Embed(title=f"r/{subreddit['name']} | {post.score} upvotes", color=0xff5700)
                    embed.add_field(name="\u200b", value=f"[{post.title}](https://www.reddit.com{post.permalink})\n")
                    embed.set_image(url=post.url)
                    await self.client.get_channel(781848069985009696).send(embed=embed)
                    self.subreddits.update_one({"name": subreddit["name"]}, {"$set": {"last_checked": datetime.now()}})


def setup(client: Client):
    timestamp = Timestamp(client)
    client.add_cog(timestamp)
    timestamp.meeting_check.start()
    timestamp.reddit_check.start()
