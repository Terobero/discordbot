from discord import Client, Embed, Member
from discord.ext import commands
from re import findall


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
        matches = findall('".+?"', string)
        if len(matches) < 3:
            embed = Embed(title=f"{string}?", color=0xff00ff)
            message = await ctx.send(embed=embed)
            await message.add_reaction("<:no:647940735479578624>")
            await message.add_reaction("<:yes:712680909559562270>")
        else:
            embed = Embed(title=f"{matches[0][1:-1]}?", color=0xff00ff)
            embed_txt = ""
            emoji_letters = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯"]
            for i, match in enumerate(matches[1:]):
                match = match[1:-1]
                embed_txt += f"{emoji_letters[i]} {match}\n\n"

            embed.add_field(name="\u200b", value=embed_txt[:-1])
            message = await ctx.send(embed=embed)
            for i in range(len(matches)-1):
                await message.add_reaction(emoji_letters[i])


def setup(client: Client):
    client.add_cog(Misc(client))
