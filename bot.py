import os
import traceback
import datetime
import math

import discord
from discord import app_commands, Interaction
from discord.ext import commands
from discord.app_commands import AppCommandError
from dotenv import load_dotenv
from libs import Database
from libs import Convert
from libs import Error
from libs import Utils
load_dotenv()

config = {
    'prefix': os.getenv('PREFIX'),
    'oauth_url': discord.utils.oauth_url(os.getenv('BOT_ID'),
                                         permissions=discord.Permissions(536870912),
                                         scopes=['bot', 'applications.commands'])
}

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        TRACEBACK_CHANNEL = await bot.fetch_channel(int(os.getenv('TRACEBACK_CHANNEL_ID')))
        ERROR_CHANNEL = await bot.fetch_channel(int(os.getenv('ERROR_CHANNEL_ID')))

        if isinstance(error, app_commands.CommandInvokeError):
            error = error.original
        elif isinstance(error, app_commands.CommandOnCooldown):
            return
        elif isinstance(error, app_commands.MissingPermissions):
            return
        elif isinstance(error, Error.NotOwner):
            return
        elif isinstance(error, discord.Forbidden):
            return await interaction.response.send_message(
                'Botの権限を確認してみてくれ。\n`最低限必要な権限`\n```\n・ウェブフックの管理\n```', ephemeral=True)
        elif isinstance(error, discord.errors.NotFound):
            return

        tracebacks = getattr(error, 'traceback', error)
        tracebacks = ''.join(traceback.TracebackException.from_exception(tracebacks).format())
        tracebacks = discord.utils.escape_markdown(tracebacks)
        embed_traceback = discord.Embed(description=f'```{tracebacks}```')
        msg_traceback = await TRACEBACK_CHANNEL.send(embed=embed_traceback)

        embed_logs = discord.Embed()
        embed_logs.set_author(name=f'{interaction.user.display_name} ({interaction.user.id})',
                              icon_url=interaction.user.avatar.url if interaction.user.avatar else 'https://cdn.discordapp.com/embed/avatars/0.png')
        embed_logs.add_field(name='command', value=interaction.command.name, inline=False)
        embed_logs.add_field(name='error', value=f'```{error}```', inline=False)
        embed_logs.add_field(name='traceback_id', value=f'```{msg_traceback.id}```')
        if interaction.channel.type == discord.ChannelType.text:
            embed_logs.set_footer(text=f'{interaction.channel.name} \nG:{interaction.guild_id} C:{interaction.channel_id}',
                                  icon_url=interaction.guild.icon.url if interaction.guild.icon else 'https://cdn.discordapp.com/embed/avatars/0.png')
        else:
            embed_logs.set_footer(text=f"{interaction.user}'s DM_CHANNEL C:{interaction.channel_id}")
        await ERROR_CHANNEL.send(embed=embed_logs)

        embed_error = discord.Embed(title='エラー発生', color=0xff0000)
        msg = 'エラーが発生した模様だ。\n コマンドが正しく入力されているにも関わらずエラーが出る時には、公式サーバーまで来てくれると助かるぞ。\n  [公式サーバー](https://discord.gg/k5Feum44gE)\n'
        embed_error.add_field(name='メッセージ', value=msg, inline=False)
        try:
            await interaction.response.send_message(embed=embed_error, ephemeral=True)
        except discord.Forbidden:
            pass

    async def setup_hook(self):
        await bot.load_extension('jishaku')
        for ext in extensions_list:
            try:
                await bot.load_extension(f'cogs.{ext}')
            except discord.ext.commands.ExtensionAlreadyLoaded:
                await bot.reload_extension(f'cogs.{ext}')

    async def get_context(self, message, *args, **kwargs):
        return await super().get_context(message, *args, **kwargs)


bot = MyBot(
    command_prefix=commands.when_mentioned_or(config['prefix']),
    intents=discord.Intents.default(),
    allowed_mentions=discord.AllowedMentions(replied_user=False, everyone=False),
    help_command=None
)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.command:
        CMD_LOG_CHANNEL = await bot.fetch_channel(int(os.getenv('CMD_LOG_CHANNEL_ID')))
        cmd_name = interaction.command.qualified_name
        embed = discord.Embed(title='Command Log')
        embed.add_field(name='Command Name', value=f'`{cmd_name}`', inline=False)
        embed.add_field(name='Author', value=f'`{interaction.user}({interaction.user.id})`', inline=False)

        bot.db.command_log_add(cmd_name)
        await CMD_LOG_CHANNEL.send(embed=embed)


@bot.event
async def on_ready():
    READY_LOG_CHANNEL = await bot.fetch_channel(int(os.getenv('READY_CHANNEL_ID')))

    print(f'{bot.user.name} でログインしました')
    print(f'サーバー数: {len(bot.guilds)}')
    now = math.floor(datetime.datetime.now(datetime.timezone.utc).timestamp())
    await READY_LOG_CHANNEL.send(f'On Ready.\nServer: {len(bot.guilds)}\nName: {bot.user.name}\n'
                                 f'Time: <t:{now}:d><t:{now}:T>')
    await bot.change_presence(
        activity=discord.Game(name=f'/stage3 | ステージ情報配信中')
    )
    await bot.tree.sync()


if __name__ == '__main__':
    bot.db = Database.Database()
    bot.convert = Convert.Convert()
    bot.utils = Utils.Utils()
    bot.config = config

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
