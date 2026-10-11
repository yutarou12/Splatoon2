import math
import sys

import discord
from discord import app_commands, ui
from discord.ext import commands

from libs.Env import OAUTH_URL


class Bot(commands.Cog):
    """主にBOTのヘルプや概要を表示するコマンドがあるカテゴリーです"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='ping')
    async def ping(self, ctx):
        """Botが反応するか確かめれるぞ!"""
        return await ctx.response.send_message(f'🏓 Pong! - {math.floor(self.bot.latency * 1000)} ms', ephemeral=True)

    @app_commands.command(name='invite')
    async def invite(self, ctx):
        """BOTの招待リンクを出すぞ!"""
        return await ctx.response.send_message(f'これが招待リンクだ。\n{OAUTH_URL}', ephemeral=True)

    @app_commands.command(name='help')
    async def _help(self, ctx):
        """Botのヘルプを表示するぞ!"""
        embed = discord.Embed(title='コマンド一覧', color=0x00ff00)
        embed.add_field(name='</ping:960404289837223986>', value='Botが反応するか確かめれるぞ。', inline=False)
        embed.add_field(name='</invite:960404290571218984>', value='BOTの招待リンクをだすぞ。', inline=False)
        embed.add_field(name='</about:960404291351379978>', value='BOTの情報を見ることが出来る。', inline=False)
        embed.add_field(name='</stage:941490889635807232>', value='Splatoon2のステージを表示するようだ。', inline=False)
        embed.add_field(name='</stage3:1018766711379476480>', value='Splatoon3のステージを表示するようだ。', inline=False)
        embed.add_field(name='</list:962729788626333707>', value='ステージ情報の一覧を表示するぞ(2のみ)。', inline=False)
        embed.add_field(name='</weapon:969392810799276142>', value='おススメのブキをブキチが教えてくれるぞ!', inline=False)
        embed.add_field(name='</auto-set:1025669000576913440>', value='ステージ情報を自動送信するチャンネルを設定するぞ。', inline=False)
        embed.add_field(name='</auto-del:1025669000576913441>', value='自動送信設定を削除するぞ。', inline=False)
        embed.add_field(name='</friend:1028822298528059464>', value='フレンドコードを表示するぞ。', inline=False)
        embed.add_field(name='</friend-setting:1028822298528059465>', value='フレンドコードの設定ができるみたいだ。', inline=False)

        view = ui.View()
        view.add_item(discord.ui.Button(
            label='プライバシーポリシー', style=discord.ButtonStyle.url, url='https://splatoon.syutarou.xyz/privacy-policy'))
        view.add_item(discord.ui.Button(
            label='利用規約', style=discord.ButtonStyle.url, url='https://splatoon.syutarou.xyz/terms/'))
        view.add_item(discord.ui.Button(
            label='コマンドヘルプ', style=discord.ButtonStyle.url, url='https://splatoon.syutarou.xyz/docs/prologue/commands/'))
        return await ctx.response.send_message(embed=embed, ephemeral=True, view=view)

    @app_commands.command(name='about')
    async def about(self, ctx):
        """BOTの情報を見れるぞ!"""
        owner = await self.bot.fetch_user((await self.bot.application_info()).team.owner_id)
        info_guilds = len(self.bot.guilds)
        auto_ch_len = len(self.bot.db.get_webhook_list())
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
                              f'/help でコマンド一覧を見ることが出来るぞ```',
                        inline=False)
        embed.add_field(name='詳細',
                        value=f'```yml\n[導入サーバー数] {info_guilds}\n[自動送信チャンネル数] {auto_ch_len}\n```',
                        inline=False)

        view = ui.View()
        view.add_item(discord.ui.Button(
            label='BOTの招待リンク', style=discord.ButtonStyle.url, url=OAUTH_URL, row=1))
        view.add_item(discord.ui.Button(
            label='サポートサーバー', style=discord.ButtonStyle.url, url='https://discord.gg/k5Feum44gE', row=1))
        view.add_item(discord.ui.Button(
            label='開発者のサイト', style=discord.ButtonStyle.url, url='https://syutarou.xyz', row=1))
        view.add_item(discord.ui.Button(
            label='プライバシーポリシー', style=discord.ButtonStyle.url, url='https://splatoon.syutarou.xyz/privacy-policy', row=2))
        view.add_item(discord.ui.Button(
            label='利用規約', style=discord.ButtonStyle.url, url='https://splatoon.syutarou.xyz/terms/', row=2))
        return await ctx.response.send_message(embed=embed, ephemeral=True, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bot(bot))
