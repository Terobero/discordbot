from discord import Client, Role
from discord.ext import commands


class Role(commands.Cog):
    def __init__(self, client: Client):
        self.client = client

    @commands.command(aliases=["cr"])
    async def create_role(self, ctx: commands.Context, *, role: str):
        for _role in ctx.guild.roles:
            if _role.name == role:
                await ctx.send(f"Role `{role}` already exists!")
                return
        await ctx.guild.create_role(name=role, mentionable=True)
        await ctx.send(f"Created role: `{role}`")

    @commands.command(aliases=["gr"])
    async def give_role(self, ctx: commands.Context, *, role: Role):
        if role.name not in [x.name for x in ctx.guild.roles]:
            await ctx.send(f"Role `{role}` doesn't exist!")
            return
        await ctx.author.add_roles(role)
        await ctx.send(f"Gave role `{role}` to {ctx.author.mention}")

    @commands.command(aliases=["rr"])
    async def remove_role(self, ctx: commands.Context, *, role: Role):
        if role.name not in [x.name for x in ctx.guild.roles]:
            await ctx.send(f"Role `{role}` doesn't exist!")
            return
        await ctx.author.remove_roles(role)
        await ctx.send(f"Removed role `{role}` from {ctx.author.mention}")


def setup(client: Client):
    client.add_cog(Role(client))
