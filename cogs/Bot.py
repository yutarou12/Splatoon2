import math
import sys
import os

import discord
from discord import app_commands
from discord.ext import commands


class Bot(commands.Cog):
    """主にBOTのヘルプや概要を表示するコマンドがあるカテゴリーです"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='ping')
    async def ping(self, ctx):
        """Botの応答速度を測ります。"""
        return await ctx.response.send_message(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms', ephemeral=True)

    @app_commands.command(name='invite')
    async def invite(self, ctx):
        """BOTの招待リンクを出します。"""
        return await ctx.response.send_message(f'招待リンクです\n{self.bot.config["oauth_url"]}', ephemeral=True)

    @app_commands.command(name='help')
    async def _help(self, ctx):
        """Botのヘルプを表示します。"""
        embed = discord.Embed(title='ヘルプ', color=0x00ff00,
                              description='```\nBeta版と書かれているものは、開発中のコマンドです。\n予期せず仕様が変わる場合がございます。ご了承ください。```\n')
        embed.add_field(name='/help', value='ヘルプを表示します。', inline=False)
        embed.add_field(name='/ping', value='Botの応答速度を測ります。', inline=False)
        embed.add_field(name='/invite', value='BOTの招待リンクを出します。', inline=False)
        embed.add_field(name='/about', value='BOTの情報を表示します。', inline=False)
        embed.add_field(name='/stage', value='Splatoon2のステージを表示します。', inline=False)
        embed.add_field(name='/stage3', value='Splatoon3のステージを表示します。(Beta版)', inline=False)
        embed.add_field(name='/list', value='ステージ情報の一覧を表示します。', inline=False)
        embed.add_field(name='/weapon', value='ブキガチャをすることが出来ます。', inline=False)
        return await ctx.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name='about')
    async def about(self, ctx):
        """BOTの情報を表示します。"""
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
                        value=f'```yml\nPython:\n{sys.version}\ndiscord.py: {discord.__version__}\n```',
                        inline=False)
        embed.add_field(name='Prefix',
                        value=f'```yml\n/ (スラッシュコマンド)\n'
                              f'/help でコマンドの説明を見ることが出来ます```',
                        inline=False)
        embed.add_field(name='詳細',
                        value=f'```yml\n[導入サーバー数] {info_guilds}\n[ユーザー数] {info_user}\n[チャンネル数] {info_ch}\n```',
                        inline=False)
        embed.add_field(name='各種リンク',
                        value=f'[BOTの招待リンク]({self.bot.config["oauth_url"]}) | '
                              '[サポートサーバー](https://discord.gg/k5Feum44gE) | '
                              '[開発者のサイト](https://syutarou.xyz)',
                        inline=False)
        return await ctx.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bot(bot))
