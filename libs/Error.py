from discord.app_commands import errors


class NotOwner(errors.CheckFailure):
    pass
