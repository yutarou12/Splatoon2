import math
import traceback
import os

from datetime import datetime

import discord
from discord import Interaction, Embed, Game, Forbidden, NotFound
from discord.app_commands import AppCommandError, CommandInvokeError, CommandOnCooldown, MissingPermissions
from discord.ext import commands

from libs.Error import NotOwner
from libs.Utils import icon_convert


class Log(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        TRACEBACK_CHANNEL = await self.bot.fetch_channel(int(os.getenv('TRACEBACK_CHANNEL_ID')))
        ERROR_CHANNEL = await self.bot.fetch_channel(int(os.getenv('ERROR_CHANNEL_ID')))

        if isinstance(error, CommandInvokeError):
            error = error.original
        elif isinstance(error, CommandOnCooldown):
            return
        elif isinstance(error, MissingPermissions):
            return
        elif isinstance(error, NotOwner):
            return
        elif isinstance(error, Forbidden):
            return await interaction.response.send_message(
                'Botの権限を確認してみてくれ。\n`最低限必要な権限`\n```\n・ウェブフックの管理\n```', ephemeral=True)
        elif isinstance(error, NotFound):
            return

        tracebacks = getattr(error, 'traceback', error)
        tracebacks = ''.join(traceback.TracebackException.from_exception(tracebacks).format())
        tracebacks = discord.utils.escape_markdown(tracebacks)
        embed_traceback = Embed(title='Traceback Log', description=f'```{tracebacks}```')
        msg_traceback = await TRACEBACK_CHANNEL.send(embed=embed_traceback)

        embed_logs = Embed(title='Error Log')
        embed_logs.set_author(name=f'{interaction.user.display_name} ({interaction.user.id})',
                              icon_url=icon_convert(interaction.user.avatar))
        embed_logs.add_field(name='Command', value=interaction.command.name, inline=False)
        embed_logs.add_field(name='Error', value=f'```{error}```', inline=False)
        embed_logs.add_field(name='TracebackID', value=f'```{msg_traceback.id}```')
        if interaction.channel.type == discord.ChannelType.text:
            embed_logs.set_footer(
                text=f'{interaction.channel.name} \nG:{interaction.guild_id} C:{interaction.channel_id}',
                icon_url=icon_convert(interaction.guild.icon))
        else:
            embed_logs.set_footer(text=f"{interaction.user}'s DM_CHANNEL C:{interaction.channel_id}")
        await ERROR_CHANNEL.send(embed=embed_logs)

        embed_error = Embed(title='エラー発生', color=0xff0000)
        msg = 'エラーが発生した模様だ。\n コマンドが正しく入力されているにも関わらずエラーが出る時には、公式サーバーまで来てくれると助かるぞ。\n  [公式サーバー](https://discord.gg/k5Feum44gE)\n'
        embed_error.add_field(name='メッセージ', value=msg, inline=False)
        try:
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
        except Forbidden:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        log_channel = await self.bot.fetch_channel(int(os.getenv('READY_CHANNEL_ID')))
        print(f'{self.bot.user.name} でログインしました')
        print(f'サーバー数: {len(self.bot.guilds)}')
        if log_channel:
            today_stamp = math.floor(datetime.utcnow().timestamp())
            embed = Embed(title='on_ready')
            embed.add_field(name='NowTime', value=f'<t:{today_stamp}:d><t:{today_stamp}:T>', inline=False)
            embed.add_field(name='Servers', value=f'{len(self.bot.guilds)}', inline=False)
            await log_channel.send(embed=embed)
        await self.bot.change_presence(
            activity=Game(name=f'/stage3 | ステージ情報配信中')
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.command:
            log_channel = await self.bot.fetch_channel(int(os.getenv('CMD_LOG_CHANNEL_ID')))
            cmd_name = interaction.command.qualified_name
            if log_channel:
                today_stamp = math.floor(datetime.utcnow().timestamp())
                embed = discord.Embed(title='Command Log')
                embed.add_field(name='Command Name', value=f'`{cmd_name}`', inline=False)
                embed.add_field(name='User', value=f'`{interaction.user}({interaction.user.id})`', inline=False)
                embed.add_field(name='Time', value=f'<t:{today_stamp}:d> <t:{today_stamp}:T>', inline=False)
                await log_channel.send(embed=embed)

            await self.bot.db.command_log_add(cmd_name)


async def setup(bot):
    await bot.add_cog(Log(bot))
