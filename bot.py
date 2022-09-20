import os
import traceback

import discord
from discord import app_commands, Interaction
from discord.ext import commands, tasks
from discord.app_commands import AppCommandError
from dotenv import load_dotenv
from libs import Database
from libs import Convert
load_dotenv()

config = {
    'prefix': os.getenv('PREFIX'),
    'token': os.getenv('DISCORD_BOT_TOKEN'),
    'oauth_url': discord.utils.oauth_url(os.getenv('BOT_ID'),
                                         permissions=discord.Permissions(0),
                                         scopes=['bot', 'applications.commands'])
}

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]

MY_GUILD = discord.Object(id=int(os.getenv('OFFICIAL_GUILD')))


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: Interaction, error: AppCommandError):
        print('--------------------------error---------------------')
        TRACEBACK_CHANNEL = await bot.fetch_channel(int(os.getenv('TRACEBACK_CHANNEL_ID')))
        OWNER = bot.application.owner

        if isinstance(error, commands.CommandInvokeError):
            error = error.original
        elif isinstance(error, app_commands.CommandOnCooldown):
            return
        elif isinstance(error, discord.errors.NotFound):
            return

        tracebacks = getattr(error, 'traceback', error)
        tracebacks = ''.join(traceback.TracebackException.from_exception(tracebacks).format())
        tracebacks = discord.utils.escape_markdown(tracebacks)
        embed_traceback = discord.Embed(description=f'```{tracebacks}```')
        msg_traceback = await TRACEBACK_CHANNEL.send(embed=embed_traceback)

        embed_logs = discord.Embed()
        embed_logs.set_author(name=f'{interaction.user.display_name} ({interaction.user.id})', icon_url=interaction.user.avatar.url)
        embed_logs.add_field(name='command', value=interaction.command.name, inline=False)
        embed_logs.add_field(name='error', value=f'```{error}```', inline=False)
        embed_logs.add_field(name='traceback_id', value=f'```{msg_traceback.id}```')
        if interaction.channel.type == discord.ChannelType.text:
            embed_logs.set_footer(text=f'{interaction.channel.name} \nG:{interaction.guild_id} C:{interaction.channel_id}',
                                  icon_url=interaction.guild.icon.url)
        else:
            embed_logs.set_footer(text=f"{interaction.user}'s DM_CHANNEL C:{interaction.channel_id}")
        await OWNER.send(embed=embed_logs)

        embed_error = discord.Embed(title='エラーが発生しました。', color=0xff0000)
        msg = 'エラーが発生しました。\n コマンドが正しく入力されているにも関わらずエラーが出る際には、公式サーバーまでお問い合わせください。\n  [公式サーバー](https://discord.gg/k5Feum44gE)\n'
        embed_error.add_field(name='メッセージ', value=msg, inline=False)
        try:
            await interaction.edit_original_response(embed=embed_error)
        except discord.Forbidden:
            pass

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)

        try:
            await bot.load_extension('jishaku')
        except discord.ext.commands.ExtensionAlreadyLoaded:
            await bot.reload_extension('jishaku')
        for ext in extensions_list:
            try:
                await bot.load_extension(f'cogs.{ext}')
            except discord.ext.commands.ExtensionAlreadyLoaded:
                await bot.reload_extension(f'cogs.{ext}')

    async def get_context(self, message, *args, **kwargs):
        return await super().get_context(message, *args, **kwargs)


intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = MyBot(
    command_prefix=commands.when_mentioned_or(config['prefix']),
    intents=intents,
    allowed_mentions=discord.AllowedMentions(replied_user=False, everyone=False),
    help_command=None
)


@bot.event
async def on_ready():
    print(f'{bot.user.name} でログインしました')
    print(f'サーバー数: {len(bot.guilds)}')
    await bot.change_presence(
        activity=discord.Game(name=f'/stage | ステージ情報配信中')
    )


if __name__ == '__main__':
    bot.db = Database.Database()
    bot.convert = Convert.Convert()
    bot.config = config

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
