from discord import Client, Member
from discord.ext import commands


async def admin_check(ctx: commands.Context):
    return ctx.author.top_role.name == "Admin"


class Admin(commands.Cog):
    def __init__(self, client: Client):
        self.client = client

    @commands.command()
    @commands.check(admin_check)
    async def clear(self, ctx: commands.Context, amount: int = 5):
        await ctx.channel.purge(limit=amount + 1)

    @commands.command()
    @commands.check(admin_check)
    async def kick(self, ctx: commands.Context, member: Member):
        if not ctx.guild.get_member_named(member.display_name):
            await ctx.send(f"I couldn't find the user `{member.display_name}` in this server!")
        elif member.top_role.name in ["Admin", "Bot"]:
            await ctx.send(f"You can't ban this user because `{member.display_name}` has ban permissions too!")
        else:
            await member.kick()

    @commands.command()
    @commands.check(admin_check)
    async def ban(self, ctx: commands.Context, member: Member):
        if not ctx.guild.get_member_named(member.display_name):
            await ctx.send(f"I couldn't find the user `{member.display_name}` in this server!")
        elif member.top_role.name in ["Admin", "Bot"]:
            await ctx.send(f"You can't ban this user because `{member.display_name}` has ban permissions too!")
        else:
            await member.ban()

    @commands.command()
    @commands.check(admin_check)
    async def unban(self, ctx: commands.Context, member: Member):
        banned_users = await ctx.guild.bans()
        for ban_entry in banned_users:
            user = ban_entry.user
            if user.name == member:
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned {user.mention}")
                return


def setup(client: Client):
    client.add_cog(Admin(client))
