import os

import discord
from discord.ext import commands

from libs import Database, Convert, Utils
from libs.Env import PREFIX, BOT_TOKEN
from cogs.Log import Log

extensions_list = [f[:-3] for f in os.listdir("./cogs") if f.endswith(".py")]


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tree.on_error = Log.on_app_command_error

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
    command_prefix=commands.when_mentioned_or(PREFIX),
    intents=discord.Intents.default(),
    allowed_mentions=discord.AllowedMentions(replied_user=False, everyone=False),
    help_command=None
)


@bot.event
async def on_ready():
    await bot.tree.sync()


if __name__ == '__main__':
    bot.db = Database.Database()
    bot.convert = Convert.Convert()
    bot.utils = Utils.Utils()

    bot.run(BOT_TOKEN)
