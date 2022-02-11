import os
from abc import ABC

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from libs import Database
load_dotenv()

config = {
    'prefix': os.getenv('PREFIX'),
    'token': os.getenv('DISCORD_BOT_TOKEN'),
    'oauth_url': discord.utils.oauth_url(os.getenv('BOT_ID'), permissions=discord.Permissions(1342565620))
}

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]


class MyBot(commands.Bot, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_context(self, message, *args, **kwargs):
        return await super().get_context(message, *args, **kwargs)


intents = discord.Intents.all()
bot = MyBot(
    command_prefix=config['prefix'],
    intents=intents,
    help_command=None
)

bot.db = Database.Database()


@tasks.loop(minutes=10)
async def pre_loop():
    await bot.wait_until_ready()
    await bot.change_presence(
        activity=discord.Game(name=f'{config["prefix"]}help | ステージ情報配信中')
    )


@bot.event
async def on_ready():
    print(f'{bot.user.name} でログインしました')
    print(f'サーバー数: {len(bot.guilds)}')
    if not pre_loop.is_running():
        pre_loop.start()


if __name__ == '__main__':
    bot.config = config
    other_extension = ['jishaku']
    for o_extension in other_extension:
        try:
            bot.load_extension(o_extension)
        except discord.ExtensionAlreadyLoaded:
            bot.reload_extension(o_extension)
    for extension in extensions_list:
        try:
            bot.load_extension(f'cogs.{extension}')
        except discord.ExtensionAlreadyLoaded:
            bot.reload_extension(f'cogs.{extension}')

    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
