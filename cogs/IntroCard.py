import os
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

import discord
from discord import app_commands, ui, Embed, Interaction, File
from discord.ext import commands


class IntroCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='card')
    async def generate_card(self, interaction: Interaction):
        view = ui.View()
        select = TypeSelect()

        for d in os.listdir(f'./Assets'):
            select.add_option(label=d, description=f'Made by {d}')

        view.add_item(select)

        embed = Embed(title='自己紹介カードを選んでください')
        return await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class TypeSelect(ui.Select):
    def __init__(self):
        super().__init__()
        self.placeholder = '種類を選択してください'

    async def callback(self, interaction: Interaction):
        card_type = self.values[0]
        select = CardSelect(card_type=card_type)
        self.view.clear_items()

        base_select = TypeSelect()
        base_select.add_option(label=card_type, default=True, description=f'Made By {card_type}')

        for d in os.listdir(f'./Assets/{self.values[0]}'):
            select.add_option(label=d[:-4])

        self.view.add_item(base_select)
        self.view.add_item(select)

        return await interaction.response.edit_message(view=self.view)

class CardSelect(ui.Select):
    def __init__(self, card_type):
        super().__init__()
        self.placeholder = 'カードを選んでください'
        self.card_type = card_type

    async def callback(self, interaction: Interaction):
        file = File(f'./Assets/{self.card_type}/{self.values[0]}.png', 'image.png')
        embed = Embed(title='この画像で生成しますか？')
        embed.set_image(url='attachment://image.png')
        return await interaction.response.edit_message(embed=embed, attachments=[file])


async def setup(bot):
    await bot.add_cog(IntroCard(bot))