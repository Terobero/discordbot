import datetime
import pickle
from bitlyshortener import Shortener
from bson.binary import Binary
from discord import Client, Embed
from discord.channel import DMChannel
from discord.ext import commands
from json import load
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from pymongo import MongoClient


class Google(commands.Cog):
    def __init__(self, client: Client):
        self.client = client
        self.user_flows = {}
        with open("api.json", "r") as f:
            f = load(f)
            cluster = MongoClient(f.get("mongodb"))
            self.users = cluster["discord"]["users"]
            self.shortener = Shortener(tokens=[f.get("bitly")])

    async def check_creds(self, ctx: commands.Context, creds: Credentials):
        user = str(ctx.author)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self.users.update_one({"name": user}, {"$set": {"creds": Binary(pickle.dumps(creds))}})
                return False
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "google_credentials.json", scopes=["https://www.googleapis.com/auth/calendar.readonly"],
                    redirect_uri="urn:ietf:wg:oauth:2.0:oob")
                auth_url, _ = flow.authorization_url(prompt='consent')

                await ctx.author.send(f"{self.shortener.shorten_urls([auth_url])[0]}"
                                      f"\nPlease enter your token by `/login <token>`")
                await ctx.send(f"You aren't authorized, I have sent you a private message! {ctx.author.mention}")

                self.user_flows[user] = flow
                return False
        return True

    @commands.command()
    async def login(self, ctx: commands.Context, creds: str):
        if type(ctx.message.channel) is not DMChannel:
            await ctx.send("You can't use this command here!")
            return

        user = str(ctx.author)
        if user in self.user_flows.keys():
            flow = self.user_flows[user]
            flow.fetch_token(code=creds)
            creds = flow.credentials
            if not self.users.find_one({"name": user}):
                self.users.insert_one({"name": user, "creds": Binary(pickle.dumps(creds))})
            else:
                self.users.update_one({"name": user}, {"$set": {"creds": Binary(pickle.dumps(creds))}})
            self.user_flows.pop(user)
            await ctx.send("You can use Google commands now!")

    @commands.command()
    async def calendar(self, ctx: commands.Context, results: int = 5):
        creds = None
        user = str(ctx.author)
        if self.users.find_one({"name": user}):
            creds = pickle.loads(Binary(self.users.find_one({"name": user})["creds"]))
        if not await self.check_creds(ctx, creds):
            return

        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + "Z"
        calendars = []
        for calendar in service.calendarList().list().execute().get("items"):
            if calendar.get("selected"):
                events_result = service.events().list(calendarId=calendar.get("id"), timeMin=now,
                                                      maxResults=results, singleEvents=True,
                                                      orderBy="startTime").execute()
                calendars.append(events_result.get("items", []))

        if not calendars:
            await ctx.send("No upcoming events found.")

        embed = Embed(title=f"{ctx.author.display_name}'s Calendar", color=0x4285f4)
        for calendar in calendars:
            for event in calendar:
                start = event["start"].get("dateTime", event["start"].get("date"))
                if "T" in start:
                    start = start.split("T")
                    start[1] = " " + start[1][0:-9]
                else:
                    start = [start, ""]

                months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                          "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
                start[0] = start[0].split("-")
                start[0] = start[0][2] + " " + months[int(start[0][1])-1] + " " + start[0][0]

                embed.add_field(name=start[0] + start[1], value=event["summary"])
        await ctx.send(embed=embed)


def setup(client: Client):
    client.add_cog(Google(client))
