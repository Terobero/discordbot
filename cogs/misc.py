from discord import Client, Member, Role
from discord.ext import commands


class Misc(commands.Cog):
    def __init__(self, client: Client):
        self.client = client

    @commands.command()
    async def ping(self, ctx: commands.Context):
        await ctx.send("pong " + ctx.author.mention)

    @commands.command()
    async def slap(self, ctx: commands.Context, members: commands.Greedy[Member], *, reason: str = 'no reason'):
        slapped = ", ".join(x.mention for x in members)
        if slapped == "":
            slapped = ctx.guild.get_member(137635405590691840).mention
        await ctx.send('{} just got slapped for {}'.format(slapped, reason))

    @commands.command()
    async def users(self, ctx: commands.Context, role: str = "@everyone"):
        if role.lower() not in [x.name.lower() for x in ctx.guild.roles]:
            await ctx.send(f"Role `{role}` doesn't exist!")
            return

        users = [x.name for x in ctx.guild.members for y in x.roles if y.name.lower() == role.lower()]
        await ctx.send(f"Users in this server with the role `{role}`:\n{', '.join(users)}")

    @commands.command()
    async def poll(self, ctx: commands.Context, *, string: str):
        if string[0] is not "\"" or string[-1] is not "\"":
            await ctx.send("Wrong poll format!")
            return

        string = ' '.join(string[1:-1].split()).split("\" \"")
        if len(string) == 1:
            pass
        else:
            pass


def setup(client: Client):
    client.add_cog(Misc(client))
