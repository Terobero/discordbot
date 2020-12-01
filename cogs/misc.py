from bs4 import BeautifulSoup
from discord import Client, Embed, Member
from discord.ext import commands
from re import findall
from requests import get


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

    @commands.command()
    async def github(self, ctx: commands.Context, username: str):
        link = f"https://github.com/{username}"
        page = get(link)
        if page.status_code != 200:
            await ctx.send(f"Can't find user `{username}` in github!")
            return

        embed = Embed(title=f"{username}'s Github", color=0x24292e)
        soup = BeautifulSoup(page.text, "html.parser")
        embed.set_thumbnail(url=soup.find("img", {"class": "avatar-user"})["src"])
        embed.add_field(name="\u200b", value=f"[{soup.find('div', {'class': 'user-profile-bio'}).text}]({link})", inline=False)
        for repo in soup.find_all("div", {"class", "pinned-item-list-item-content"}):
            repo_name = repo.find("span").text.strip()
            repo_desc = repo.find("p", {"class": "pinned-item-desc"}).text.strip()
            repo_lang = repo.find("span", {"itemprop": "programmingLanguage"})
            if repo_desc:
                repo_desc = " | " + repo_desc
            if repo_lang:
                repo_lang = f"💻 {repo_lang.text.strip()}"
            else:
                repo_lang = ""
            stars_forks = repo.find_all("a", {"class": "pinned-item-meta"})
            repo_star = None
            repo_fork = None
            repo_link = f"[Link](https://github.com{repo.find('a', href=True)['href']})"
            for i in stars_forks:
                i = str(i)
                if "aria-label=\"star" in i and "aria-label=\"fork" in i:
                    repo_star = repo.find_all("a", {"class": "pinned-item-meta"})[0].text.strip()
                    repo_fork = repo.find_all("a", {"class": "pinned-item-meta"})[1].text.strip()
                elif "aria-label=\"star" in i:
                    repo_star = repo.find("a", {"class": "pinned-item-meta"}).text.strip()
                elif "aria-label=\"fork" in i:
                    repo_fork = repo.find("a", {"class": "pinned-item-meta"}).text.strip()
            if repo_star and repo_fork:
                embed.add_field(name=repo_name, value=f"{repo_link}{repo_desc}\n{repo_lang} | ⭐ {repo_star} | 🍴 {repo_fork}")
            elif repo_star:
                embed.add_field(name=repo_name, value=f"{repo_link}{repo_desc}\n{repo_lang} | ⭐ {repo_star}")
            elif repo_fork:
                embed.add_field(name=repo_name, value=f"{repo_link}{repo_desc}\n{repo_lang} | 🍴 {repo_fork}")
            else:
                embed.add_field(name=repo_name, value=f"{repo_link}{repo_desc}\n{repo_lang}")
        await ctx.send(embed=embed)


def setup(client: Client):
    client.add_cog(Misc(client))
