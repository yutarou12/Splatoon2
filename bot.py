import os
from abc import ABC

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from libs import Database
from libs import Convert
load_dotenv()

config = {
    'prefix': os.getenv('PREFIX'),
    'token': os.getenv('DISCORD_BOT_TOKEN'),
    'oauth_url': discord.utils.oauth_url(os.getenv('BOT_ID'),
                                         permissions=discord.Permissions(277025778752),
                                         scopes=['bot', 'applications.commands'])
}

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]


class MyBot(commands.Bot, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def get_context(self, message, *args, **kwargs):
        return await super().get_context(message, *args, **kwargs)


intents = discord.Intents.default()
intents.guilds = True

bot = MyBot(
    command_prefix=config['prefix'],
    intents=intents,
    allowed_mentions=discord.AllowedMentions(replied_user=False, everyone=False)
)


@bot.event
async def on_ready():
    print(f'{bot.user.name} でログインしました')
    print(f'サーバー数: {len(bot.guilds)}')
    await bot.change_presence(
        activity=discord.Game(name=f'{config["prefix"]}help | ステージ情報配信中')
    )


if __name__ == '__main__':
    bot.db = Database.Database()
    bot.convert = Convert.Convert()
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
