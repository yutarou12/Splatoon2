import os
import discord
from dotenv import load_dotenv

load_dotenv()

PREFIX: str = os.getenv('PREFIX', '!')
BOT_ID: int = int(os.getenv('BOT_ID', "0"))
BOT_TOKEN: str = os.getenv('DISCORD_BOT_TOKEN', "")
OAUTH_URL: str = discord.utils.oauth_url(BOT_ID,
                                    permissions=discord.Permissions(536870912),
                                    scopes=['bot', 'applications.commands'])
TRACEBACK_CHANNEL_ID: int = int(os.getenv('TRACEBACK_CHANNEL_ID', 0))
ERROR_CHANNEL_ID: int = int(os.getenv('ERROR_CHANNEL_ID', 0))
READY_CHANNEL_ID: int = int(os.getenv('READY_CHANNEL_ID', 0))
CMD_LOG_CHANNEL_ID: int = int(os.getenv('CMD_LOG_CHANNEL_ID', 0))

LOG_WEBHOOK_URL: str = os.getenv('LOG_WEBHOOK_URL', '')
