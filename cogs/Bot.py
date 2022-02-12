import math
import sys

import discord
from discord.ext import commands


class Bot(commands.Cog):
    """主にBOTのヘルプや概要を表示するコマンドがあるカテゴリーです"""
    def __init__(self, bot):
        self.bot: discord.Bot = bot

    @commands.command(description='Botの応答速度を測ります')
    async def ping(self, ctx):
        await ctx.reply(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms',
                        allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの招待リンクを出します')
    async def invite(self, ctx):
        return await ctx.reply(f'招待リンクです\n{self.bot.config["oauth_url"]}',
                               allowed_mentions=discord.AllowedMentions.none())

    @commands.command(description='BOTの情報を表示します')
    async def about(self, ctx):

        owner = await self.bot.fetch_user((await self.bot.application_info()).owner.id)
        info_guilds = len(self.bot.guilds)
        info_user = len(self.bot.users)
        info_ch = 0
        for guild in self.bot.guilds:
            info_ch += len(guild.channels)
        embed = discord.Embed(title=f'{self.bot.user}')
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.add_field(name='開発者',
                        value=f'```c\n# discord: {owner}\n```',
                        inline=False)
        embed.add_field(name='開発言語',
                        value=f'```yml\nPython:\n{sys.version}\nPycord: {discord.__version__}\n```',
                        inline=False)
        embed.add_field(name='Prefix',
                        value=f'```yml\n{self.bot.config["prefix"]}\n'
                              f'{self.bot.config["prefix"]}help でコマンドの説明を見ることが出来ます```',
                        inline=False)
        embed.add_field(name='詳細',
                        value=f'```yml\n[導入サーバー数] {info_guilds}\n[ユーザー数] {info_user}\n[チャンネル数] {info_ch}\n```',
                        inline=False)
        embed.add_field(name='各種リンク',
                        value=f'[BOTの招待リンク]({self.bot.config["oauth_url"]}) | '
                              '[公式サーバー](https://discord.gg/k5Feum44gE) | '
                              '[開発者のサイト](https://syutarou.xyz)',
                        inline=False)
        await ctx.reply(embed=embed, allowed_mentions=discord.AllowedMentions.none())


def setup(bot):
    bot.add_cog(Bot(bot))
