import os
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

import discord
from discord import app_commands, ui, Embed, Interaction, File, ButtonStyle
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
        embed = Embed(title='この画像で生成しますか？', description='`画像を変更する場合は再度セレクトボックスから選んでください`')
        embed.set_image(url='attachment://image.png')

        self.view.add_item(CheckButton(
            label='はい', style=ButtonStyle.green, custom_id='1', data={"type": self.card_type, "name": self.values[0]}))
        self.view.add_item(CheckButton(label='いいえ', style=ButtonStyle.red, custom_id='0', data={}))
        return await interaction.response.edit_message(embed=embed, attachments=[file], view=self.view)


class CheckButton(ui.Button):
    def __init__(self, data: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data

    async def callback(self, interaction: Interaction):
        embed = interaction.message.embeds[0]
        if not int(self.custom_id):
            embed.title = 'キャンセルしました'
            return await interaction.response.edit_message(view=None, embed=embed, attachments=[])
        else:
            embed.title = '編集する項目を選んでください'
            view = ui.View()
            select = EditFieldSelect()

            with open('./data/assets_data.json', 'r', encoding='utf-8') as f:
                base_data = json.load(f)

            card_data = (base_data.get(self.data.get("type"))).get(self.data.get("name"))
            for d in card_data.get("fields"):
                select.add_option(label=d)
                

            view.add_item(select)
            return await interaction.response.edit_message(view=view, embed=embed, attachments=[])


class EditFieldSelect(ui.Select):
    def __init__(self):
        super().__init__()
        self.placeholder = '編集する項目を選択'

    async def callback(self, interaction: Interaction):
        selected = self.values[0]
        modal = EditFieldModal(selected=selected)
        await interaction.response.send_modal(modal)
        wait_value = await modal.wait()
        if wait_value is None:
            # Send a followup message to the channel.
            return await interaction.followup.send(f"{interaction.user} did not enter a value in time.")
        embed = interaction.message.embeds[0]
        embed.add_field(name=modal.selected, value=modal.value, inline=False)
        await modal.interaction.response.edit_message(embed=embed)

class EditFieldModal(ui.Modal):
    def __init__(self, selected, *args, **kwargs):
        super().__init__(title="編集画面", *args, **kwargs)
        self.selected = selected
        self.cache_user_data = dict()
        self.feedback = ui.TextInput(
            label=f'{selected} を入れて下さい。'
        )
        self.add_item(self.feedback)
        self.value = None
        self.interaction = None


    async def on_submit(self, interaction: Interaction, /):
        print(self.cache_user_data.get(interaction.user.id))
        if not self.cache_user_data.get(interaction.user.id):
            self.cache_user_data[interaction.user.id] = {self.selected: self.feedback.value}
        else:
            self.cache_user_data[interaction.user.id][self.selected] = self.feedback.value
        print(self.cache_user_data.get(interaction.user.id))
        self.value = self.cache_user_data[interaction.user.id]
        self.interaction = interaction
        self.stop()

async def setup(bot):
    await bot.add_cog(IntroCard(bot))